"""
Sahil Nawaz Portfolio — Backend API Routes (Phase 1)
Handles:
  - System Health: GET /api/health
  - Projects API:   GET /api/projects
  - Single Project: GET /api/projects/<int:project_id>
  - Contact API:    POST /api/contact
"""

import re
from datetime import datetime
from flask import Blueprint, request, jsonify

api_bp = Blueprint("api", __name__, url_prefix="/api")

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

# Authentic portfolio projects (as showcased in Step 06)
PROJECTS_DATA = [
    {
        "id": 1,
        "title": "Crowd Density Counting System",
        "description": "A technology-based computer vision system designed to monitor, track, and accurately estimate crowd density in public spaces.",
        "category": "ai-ml",
        "technologies": ["Python", "YOLOv8", "OpenCV", "NumPy"],
        "github_url": "https://github.com/sahilnawaz257",
        "featured": True
    },
    {
        "id": 2,
        "title": "Library Management Software",
        "description": "A software solution built to manage library book catalogues, student attendance, borrowing transactions, and inventory records.",
        "category": "software",
        "technologies": ["Python", "SQL", "Database Design"],
        "github_url": "https://github.com/sahilnawaz257",
        "featured": True
    },
    {
        "id": 3,
        "title": "Brand Guideline Audit Tool",
        "description": "A developer tool designed to verify frontend brand guideline consistency, token compliance, and typography alignment.",
        "category": "frontend",
        "technologies": ["HTML5", "CSS3", "JavaScript"],
        "github_url": "https://github.com/sahilnawaz257",
        "featured": True
    }
]

# In-memory store for Phase 1 contact submissions (prepared for SQLite integration in Phase 2)
SUBMITTED_MESSAGES = []


@api_bp.route("/health", methods=["GET"])
def health_check():
    """System health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Sahil Nawaz Portfolio API",
        "phase": "Phase 1 (Flask Backend + Frontend Integration)",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


@api_bp.route("/projects", methods=["GET"])
def list_projects():
    """Return all projects, with optional category or featured filter."""
    category = request.args.get("category", "").strip().lower()
    featured = request.args.get("featured", "").strip().lower() in ("true", "1", "yes")

    filtered = PROJECTS_DATA
    if category and category != "all":
        filtered = [p for p in filtered if p["category"] == category]
    if featured:
        filtered = [p for p in filtered if p["featured"]]

    return jsonify({
        "success": True,
        "count": len(filtered),
        "projects": filtered
    }), 200


@api_bp.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    """Return details for a single project by ID."""
    project = next((p for p in PROJECTS_DATA if p["id"] == project_id), None)
    if not project:
        return jsonify({
            "success": False,
            "error": "Project not found"
        }), 404

    return jsonify({
        "success": True,
        "project": project
    }), 200


@api_bp.route("/contact", methods=["POST"])
def submit_contact():
    """
    Accept, validate, and process contact form submissions.
    Phase 1: Rigorous backend validation with in-memory handling.
    Phase 2: Will persist to SQLite database via models.py.
    """
    # Accept both JSON payloads and Form submissions
    data = request.get_json(silent=True) or request.form.to_dict()

    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request body. JSON or Form data expected."
        }), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()

    # 1. Full Name Validation
    if not name:
        return jsonify({
            "success": False,
            "error": "Full Name is required.",
            "field": "name"
        }), 400
    if len(name) < 2:
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
            "error": "Please provide a valid email address format (e.g., sahil@example.com).",
            "field": "email"
        }), 400

    # 3. Subject Validation (Optional, max 150 chars)
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

    # Store in memory for Phase 1
    # [PHASE 2 READY]: In Phase 2, this will call Contact.create(name=name, email=email, subject=subject, message=message)
    submission_entry = {
        "id": len(SUBMITTED_MESSAGES) + 1,
        "name": name,
        "email": email,
        "subject": subject or "Forward Deployed Opportunity / Project Collaboration",
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    SUBMITTED_MESSAGES.append(submission_entry)

    return jsonify({
        "success": True,
        "message": f"Thank you, {name}! Your message has been verified and received by the Flask backend.",
        "note": "Phase 1 backend verification complete. SQLite database storage will be integrated in Phase 2.",
        "received_data": {
            "name": name,
            "email": email,
            "subject": submission_entry["subject"],
            "timestamp": submission_entry["timestamp"]
        }
    }), 201
