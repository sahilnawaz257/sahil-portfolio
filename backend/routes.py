import re
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import Contact, Project

api_bp = Blueprint("api", __name__, url_prefix="/api")

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

@api_bp.route("/health", methods=["GET"])
def health_check():
    """System health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Sahil Nawaz Portfolio API",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

@api_bp.route("/projects", methods=["GET"])
def list_projects():
    """Return all projects, with optional category or featured filter."""
    category = request.args.get("category")
    featured = request.args.get("featured", "").lower() in ("true", "1", "yes")

    try:
        projects = Project.get_all(category=category, featured_only=featured)
        return jsonify({
            "success": True,
            "count": len(projects),
            "projects": projects
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve projects",
            "details": str(e)
        }), 500

@api_bp.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    """Return details for a single project."""
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
    """Receive and store a contact message from the frontend form."""
    data = request.get_json(silent=True) or request.form

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    # Input validations
    if not name:
        return jsonify({"success": False, "error": "Name is required."}), 400

    if not email or not re.match(EMAIL_REGEX, email):
        return jsonify({"success": False, "error": "A valid email address is required."}), 400

    if not message:
        return jsonify({"success": False, "error": "Message content cannot be empty."}), 400

    if len(message) < 5:
        return jsonify({"success": False, "error": "Message is too short (minimum 5 characters)."}), 400

    try:
        contact_id = Contact.create(name=name, email=email, subject=subject, message=message)
        return jsonify({
            "success": True,
            "message": f"Thank you, {name}! Your message has been received.",
            "contact_id": contact_id
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to save message. Please try again or reach out directly via email.",
            "details": str(e)
        }), 500

@api_bp.route("/messages", methods=["GET"])
def get_messages():
    """Retrieve submitted messages for Sahil's admin review."""
    try:
        messages = Contact.get_all()
        return jsonify({
            "success": True,
            "count": len(messages),
            "messages": messages
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route("/messages/<int:message_id>/read", methods=["PATCH", "POST"])
def mark_message_read(message_id):
    """Mark a message as read."""
    try:
        updated = Contact.mark_as_read(message_id)
        if not updated:
            return jsonify({"success": False, "error": "Message not found"}), 404
        return jsonify({"success": True, "message": "Marked as read."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route("/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    """Delete a message."""
    try:
        deleted = Contact.delete(message_id)
        if not deleted:
            return jsonify({"success": False, "error": "Message not found"}), 404
        return jsonify({"success": True, "message": "Message deleted."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

