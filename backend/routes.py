"""
Sahil Nawaz Portfolio — Backend API Routes (Phase 3)
Security hardened:
- CSRF Protection on Mutating Admin Endpoints
- In-Memory Sliding Window Rate Limiting (Spam & Brute Force Prevention)
- Input Sanitization (XSS Prevention)
- Server-Side Regex & Length Validations
- Session Cookie Authentication with PBKDF2 Password Hashing
"""

import html
import re
import secrets
import time
from collections import defaultdict
from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, session
from models import ContactMessage, Project, AdminUser

api_bp = Blueprint("api", __name__, url_prefix="/api")

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

# ------------------------------------------------------------------------------
# Rate Limiting (In-Memory Sliding Window)
# ------------------------------------------------------------------------------
RATE_LIMIT_STORE = defaultdict(list)

def check_rate_limit(key, limit=10, window=60):
    """
    Check if a key (e.g. IP address + endpoint) exceeds limit requests within window seconds.
    Returns True if request is allowed, False if limit exceeded.
    """
    now = time.time()
    timestamps = [t for t in RATE_LIMIT_STORE[key] if now - t < window]
    RATE_LIMIT_STORE[key] = timestamps
    if len(timestamps) >= limit:
        return False
    RATE_LIMIT_STORE[key].append(now)
    return True


def get_client_ip():
    """Retrieve client IP address taking into account reverse proxy headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


# ------------------------------------------------------------------------------
# Authentication & CSRF Decorator
# ------------------------------------------------------------------------------
def admin_required(f):
    """
    Decorator to protect admin routes:
    1. Verifies active server-side admin session.
    2. Validates X-CSRF-Token header on state-mutating requests (POST, PUT, DELETE).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Session verification
        if not session.get("admin_logged_in"):
            return jsonify({
                "success": False,
                "error": "Unauthorized. Admin session required."
            }), 401

        # 2. CSRF Token verification for mutating requests
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            client_csrf = request.headers.get("X-CSRF-Token") or (request.get_json(silent=True) or {}).get("csrf_token")
            session_csrf = session.get("csrf_token")

            if not session_csrf or not client_csrf or not secrets.compare_digest(str(client_csrf), str(session_csrf)):
                return jsonify({
                    "success": False,
                    "error": "Forbidden. Missing or invalid CSRF token."
                }), 403

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
        "phase": "Phase 3 (Security, Final Testing & Deployment Ready)",
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
    Accept, validate, sanitize, and store contact form submissions into SQLite.
    Protected with rate limiting and strict server-side validation.
    """
    # Rate limit check: Max 8 submissions per minute per IP
    client_ip = get_client_ip()
    if not check_rate_limit(f"contact:{client_ip}", limit=8, window=60):
        return jsonify({
            "success": False,
            "error": "Rate limit exceeded. Please wait a minute before submitting again."
        }), 429

    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request body. JSON or form data expected."
        }), 400

    # Accept both full_name and name
    raw_name = str(data.get("full_name") or data.get("name") or "").strip()
    raw_email = str(data.get("email", "")).strip()
    raw_subject = str(data.get("subject", "")).strip()
    raw_message = str(data.get("message", "")).strip()

    # 1. Full Name Validation
    if not raw_name:
        return jsonify({
            "success": False,
            "error": "Full Name is required.",
            "field": "name"
        }), 400
    if len(raw_name) < 2:
        return jsonify({
            "success": False,
            "error": "Full Name must be at least 2 characters.",
            "field": "name"
        }), 400
    if len(raw_name) > 100:
        return jsonify({
            "success": False,
            "error": "Full Name cannot exceed 100 characters.",
            "field": "name"
        }), 400

    # 2. Email Address Validation
    if not raw_email:
        return jsonify({
            "success": False,
            "error": "Email address is required.",
            "field": "email"
        }), 400
    if not re.match(EMAIL_REGEX, raw_email):
        return jsonify({
            "success": False,
            "error": "Please provide a valid email address (e.g. sahil@example.com).",
            "field": "email"
        }), 400
    if len(raw_email) > 120:
        return jsonify({
            "success": False,
            "error": "Email address is too long.",
            "field": "email"
        }), 400

    # 3. Subject Validation
    if raw_subject and len(raw_subject) > 150:
        return jsonify({
            "success": False,
            "error": "Subject must not exceed 150 characters.",
            "field": "subject"
        }), 400

    # 4. Message Validation
    if not raw_message:
        return jsonify({
            "success": False,
            "error": "Message content is required.",
            "field": "message"
        }), 400
    if len(raw_message) < 10:
        return jsonify({
            "success": False,
            "error": "Message is too short. Please provide at least 10 characters.",
            "field": "message"
        }), 400
    if len(raw_message) > 2000:
        return jsonify({
            "success": False,
            "error": "Message cannot exceed 2000 characters.",
            "field": "message"
        }), 400

    # Sanitize inputs to prevent stored XSS
    full_name = html.escape(raw_name)
    email = html.escape(raw_email)
    subject = html.escape(raw_subject) if raw_subject else "Forward Deployed Opportunity / Project Collaboration"
    message = html.escape(raw_message)

    # Save to SQLite Database
    try:
        msg_id = ContactMessage.create(
            full_name=full_name,
            email=email,
            subject=subject,
            message=message
        )

        return jsonify({
            "success": True,
            "message": f"Thank you, {raw_name}! Your message has been received and securely stored.",
            "contact_id": msg_id,
            "stored_data": {
                "id": msg_id,
                "full_name": full_name,
                "email": email,
                "subject": subject,
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
# Admin Dashboard Authentication & Management APIs (PART 5 & Phase 3 Security)
# ==============================================================================

@api_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """
    Verify admin credentials with PBKDF2 hash checking.
    Throttled against brute-force attacks (max 5 attempts per minute per IP).
    Issues a cryptographically secure CSRF token upon successful authentication.
    """
    client_ip = get_client_ip()
    if not check_rate_limit(f"login:{client_ip}", limit=5, window=60):
        return jsonify({
            "success": False,
            "error": "Too many login attempts. Please wait 60 seconds before trying again."
        }), 429

    data = request.get_json(silent=True) or request.form.to_dict()
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Username and password are required."
        }), 400

    if AdminUser.verify_password(username, password):
        # Establish authenticated session
        session["admin_logged_in"] = True
        session["admin_user"] = username

        # Generate fresh CSRF token
        csrf_token = secrets.token_hex(32)
        session["csrf_token"] = csrf_token

        return jsonify({
            "success": True,
            "message": "Admin authenticated successfully.",
            "user": username,
            "csrf_token": csrf_token
        }), 200

    return jsonify({
        "success": False,
        "error": "Invalid admin username or password."
    }), 401


@api_bp.route("/admin/logout", methods=["POST"])
def admin_logout():
    """Clear admin session and invalidate CSRF token."""
    session.pop("admin_logged_in", None)
    session.pop("admin_user", None)
    session.pop("csrf_token", None)
    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200


@api_bp.route("/admin/status", methods=["GET"])
def admin_status():
    """
    Check current authentication state.
    Returns existing or renewed CSRF token if session is valid.
    """
    is_authenticated = bool(session.get("admin_logged_in"))
    csrf_token = None

    if is_authenticated:
        csrf_token = session.get("csrf_token")
        if not csrf_token:
            csrf_token = secrets.token_hex(32)
            session["csrf_token"] = csrf_token

    return jsonify({
        "authenticated": is_authenticated,
        "username": session.get("admin_user", "") if is_authenticated else None,
        "csrf_token": csrf_token
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
    """Delete a contact message by ID (protected with CSRF)."""
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
    """Add a new project record into SQLite (protected with CSRF)."""
    data = request.get_json(silent=True) or request.form.to_dict()

    raw_title = str(data.get("title", "")).strip()
    raw_desc = str(data.get("description", "")).strip()
    raw_tech = str(data.get("technologies", "")).strip()
    raw_github = str(data.get("github_url", "")).strip()
    raw_demo = str(data.get("live_demo_url", "")).strip()

    if not raw_title:
        return jsonify({"success": False, "error": "Project title is required."}), 400
    if not raw_desc:
        return jsonify({"success": False, "error": "Project description is required."}), 400
    if not raw_tech:
        return jsonify({"success": False, "error": "Technologies are required."}), 400

    # Sanitize inputs
    title = html.escape(raw_title)
    description = html.escape(raw_desc)
    technologies = html.escape(raw_tech)
    github_url = raw_github
    live_demo_url = raw_demo

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
    """Edit an existing project record (protected with CSRF)."""
    data = request.get_json(silent=True) or request.form.to_dict()

    raw_title = str(data.get("title", "")).strip()
    raw_desc = str(data.get("description", "")).strip()
    raw_tech = str(data.get("technologies", "")).strip()
    raw_github = str(data.get("github_url", "")).strip()
    raw_demo = str(data.get("live_demo_url", "")).strip()

    if not raw_title or not raw_desc or not raw_tech:
        return jsonify({"success": False, "error": "Title, description, and technologies are required."}), 400

    # Sanitize inputs
    title = html.escape(raw_title)
    description = html.escape(raw_desc)
    technologies = html.escape(raw_tech)
    github_url = raw_github
    live_demo_url = raw_demo

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
    """Delete a project record with confirmation (protected with CSRF)."""
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
