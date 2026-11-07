"""
Sahil Nawaz Portfolio — Backend API Routes (Phase 2)
Integrates SQLite Database, Contact Form Storage, Dynamic Projects API,
and Protected Admin Dashboard Endpoints.
"""

import re
from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, session
from models import ContactMessage, Project, AdminUser

api_bp = Blueprint("api", __name__, url_prefix="/api")

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def admin_required(f):
    """Decorator to protect admin routes using server-side session authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({
                "success": False,
                "error": "Unauthorized. Admin session required."
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# ==============================================================================
# Public APIs
# ==============================================================================

@api_bp.route("/health", methods=["GET"])
def health_check():
    """System health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Sahil Nawaz Portfolio API",
        "phase": "Phase 2 (SQLite Database + Full Integration)",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


@api_bp.route("/projects", methods=["GET"])
def list_projects():
    """Retrieve all projects dynamically from SQLite database."""
    try:
        projects = Project.get_all()
        return jsonify({
            "success": True,
            "count": len(projects),
            "projects": projects
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve projects from database.",
            "details": str(e)
        }), 500


@api_bp.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    """Retrieve details for a single project by ID."""
    try:
        project = Project.get_by_id(project_id)
        if not project:
            return jsonify({
                "success": False,
                "error": "Project not found"
            }), 404

        return jsonify({
            "success": True,
            "project": project
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/contact", methods=["POST"])
def submit_contact():
    """
    Accept, validate, and store contact form submissions into SQLite database.
    Ensures message is actually saved before returning a 201 Created success response.
    """
    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request body. JSON or form data expected."
        }), 400

    # Accept both full_name and name
    full_name = str(data.get("full_name") or data.get("name") or "").strip()
    email = str(data.get("email", "")).strip()
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()

    # 1. Full Name Validation
    if not full_name:
        return jsonify({
            "success": False,
            "error": "Full Name is required.",
            "field": "name"
        }), 400
    if len(full_name) < 2:
        return jsonify({
            "success": False,
            "error": "Full Name must be at least 2 characters.",
            "field": "name"
        }), 400

    # 2. Email Address Validation
    if not email:
        return jsonify({
            "success": False,
            "error": "Email address is required.",
            "field": "email"
        }), 400
    if not re.match(EMAIL_REGEX, email):
        return jsonify({
            "success": False,
            "error": "Please provide a valid email address (e.g. sahil@example.com).",
            "field": "email"
        }), 400

    # 3. Subject Validation
    if subject and len(subject) > 150:
        return jsonify({
            "success": False,
            "error": "Subject must not exceed 150 characters.",
            "field": "subject"
        }), 400

    # 4. Message Validation
    if not message:
        return jsonify({
            "success": False,
            "error": "Message content is required.",
            "field": "message"
        }), 400
    if len(message) < 10:
        return jsonify({
            "success": False,
            "error": "Message is too short. Please provide at least 10 characters.",
            "field": "message"
        }), 400
    if len(message) > 1000:
        return jsonify({
            "success": False,
            "error": "Message cannot exceed 1000 characters.",
            "field": "message"
        }), 400

    # Save to SQLite Database
    try:
        msg_id = ContactMessage.create(
            full_name=full_name,
            email=email,
            subject=subject or "Forward Deployed Opportunity / Project Collaboration",
            message=message
        )

        return jsonify({
            "success": True,
            "message": f"Thank you, {full_name}! Your message has been received and securely stored in the database.",
            "contact_id": msg_id,
            "stored_data": {
                "id": msg_id,
                "full_name": full_name,
                "email": email,
                "subject": subject or "Forward Deployed Opportunity / Project Collaboration",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Database error while saving message. Please try again or email directly.",
            "details": str(e)
        }), 500


# ==============================================================================
# Admin Dashboard Authentication & Management APIs (PART 5)
# ==============================================================================

@api_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """Verify admin credentials and set session cookie."""
    data = request.get_json(silent=True) or request.form.to_dict()
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Username and password are required."
        }), 400

    if AdminUser.verify_password(username, password):
        session["admin_logged_in"] = True
        session["admin_user"] = username
        return jsonify({
            "success": True,
            "message": "Admin authenticated successfully.",
            "user": username
        }), 200

    return jsonify({
        "success": False,
        "error": "Invalid admin username or password."
    }), 401


@api_bp.route("/admin/logout", methods=["POST"])
def admin_logout():
    """Clear admin session."""
    session.pop("admin_logged_in", None)
    session.pop("admin_user", None)
    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200


@api_bp.route("/admin/status", methods=["GET"])
def admin_status():
    """Check current authentication state."""
    is_authenticated = bool(session.get("admin_logged_in"))
    return jsonify({
        "authenticated": is_authenticated,
        "username": session.get("admin_user", "") if is_authenticated else None
    }), 200


@api_bp.route("/admin/messages", methods=["GET"])
@admin_required
def admin_get_messages():
    """Retrieve all contact form messages from SQLite."""
    try:
        messages = ContactMessage.get_all()
        return jsonify({
            "success": True,
            "count": len(messages),
            "messages": messages
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to fetch messages from database.",
            "details": str(e)
        }), 500


@api_bp.route("/admin/messages/<int:msg_id>", methods=["DELETE"])
@admin_required
def admin_delete_message(msg_id):
    """Delete a contact message by ID."""
    try:
        deleted = ContactMessage.delete(msg_id)
        if not deleted:
            return jsonify({
                "success": False,
                "error": "Message not found."
            }), 404

        return jsonify({
            "success": True,
            "message": f"Message #{msg_id} deleted successfully."
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/admin/projects", methods=["POST"])
@admin_required
def admin_create_project():
    """Add a new project record into SQLite."""
    data = request.get_json(silent=True) or request.form.to_dict()

    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    technologies = str(data.get("technologies", "")).strip()
    github_url = str(data.get("github_url", "")).strip()
    live_demo_url = str(data.get("live_demo_url", "")).strip()

    if not title:
        return jsonify({"success": False, "error": "Project title is required."}), 400
    if not description:
        return jsonify({"success": False, "error": "Project description is required."}), 400
    if not technologies:
        return jsonify({"success": False, "error": "Technologies are required."}), 400

    try:
        proj_id = Project.create(
            title=title,
            description=description,
            technologies=technologies,
            github_url=github_url,
            live_demo_url=live_demo_url
        )
        return jsonify({
            "success": True,
            "message": "Project created successfully.",
            "project_id": proj_id
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to create project in database.",
            "details": str(e)
        }), 500


@api_bp.route("/admin/projects/<int:project_id>", methods=["PUT"])
@admin_required
def admin_update_project(project_id):
    """Edit an existing project record."""
    data = request.get_json(silent=True) or request.form.to_dict()

    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    technologies = str(data.get("technologies", "")).strip()
    github_url = str(data.get("github_url", "")).strip()
    live_demo_url = str(data.get("live_demo_url", "")).strip()

    if not title or not description or not technologies:
        return jsonify({"success": False, "error": "Title, description, and technologies are required."}), 400

    try:
        updated = Project.update(
            project_id=project_id,
            title=title,
            description=description,
            technologies=technologies,
            github_url=github_url,
            live_demo_url=live_demo_url
        )
        if not updated:
            return jsonify({"success": False, "error": "Project not found."}), 404

        return jsonify({
            "success": True,
            "message": "Project updated successfully."
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to update project.",
            "details": str(e)
        }), 500


@api_bp.route("/admin/projects/<int:project_id>", methods=["DELETE"])
@admin_required
def admin_delete_project(project_id):
    """Delete a project record with confirmation."""
    try:
        deleted = Project.delete(project_id)
        if not deleted:
            return jsonify({"success": False, "error": "Project not found."}), 404

        return jsonify({
            "success": True,
            "message": f"Project #{project_id} deleted successfully."
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to delete project.",
            "details": str(e)
        }), 500
