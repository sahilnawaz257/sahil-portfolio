"""
Sahil Nawaz Portfolio — Backend API Routes
Public REST APIs for Developer Portfolio:
- /api/health    : Health and service status
- /api/projects  : Dynamic projects retrieval from SQLite
- /api/contact   : Rate-limited, sanitized contact submission persisting to SQLite
"""

import html
import re
import time
from collections import defaultdict
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import ContactMessage, Project

api_bp = Blueprint("api", __name__, url_prefix="/api")

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

# ------------------------------------------------------------------------------
# Rate Limiting (In-Memory Sliding Window for Spam Prevention)
# ------------------------------------------------------------------------------
RATE_LIMIT_STORE = defaultdict(list)

def check_rate_limit(key, limit=8, window=60):
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


# ==============================================================================
# Public APIs
# ==============================================================================

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
    Protected with sliding-window rate limiting and strict server-side validation.
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
