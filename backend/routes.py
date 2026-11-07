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
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from models import ContactMessage, Project, MeetingBooking
import email_service

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

        # Dispatch Email Notification to Sahil Nawaz (falls back safely if SMTP not configured)
        email_result = email_service.send_contact_notification(
            name=raw_name,
            email=raw_email,
            subject=raw_subject or "Portfolio Inquiry",
            message=raw_message
        )

        return jsonify({
            "success": True,
            "message": f"Thank you, {raw_name}! Your message has been received and securely stored.",
            "contact_id": msg_id,
            "email_notification": email_result,
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
# Google Meet Scheduling APIs
# ==============================================================================

@api_bp.route("/meetings/book", methods=["POST"])
def book_meeting():
    """
    Schedule a Google Meet appointment.
    Validates name, email, purpose, future date, and time slot.
    Checks for duplicate requests and dispatches notification to sahilnawaz257@gmail.com.
    """
    client_ip = get_client_ip()
    if not check_rate_limit(f"meeting:{client_ip}", limit=8, window=60):
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

    raw_name = str(data.get("full_name") or data.get("name") or "").strip()
    raw_email = str(data.get("email", "")).strip()
    raw_purpose = str(data.get("purpose", "")).strip()
    raw_date = str(data.get("meeting_date") or data.get("date") or "").strip()
    raw_time = str(data.get("meeting_time") or data.get("time") or "").strip()
    raw_notes = str(data.get("notes", "")).strip()

    # 1. Name validation
    if not raw_name or len(raw_name) < 2 or len(raw_name) > 100:
        return jsonify({
            "success": False,
            "error": "Full Name is required (2–100 characters).",
            "field": "full_name"
        }), 400

    # 2. Email validation
    if not raw_email or not re.match(EMAIL_REGEX, raw_email) or len(raw_email) > 120:
        return jsonify({
            "success": False,
            "error": "Please provide a valid email address.",
            "field": "email"
        }), 400

    # 3. Purpose validation
    if not raw_purpose or len(raw_purpose) < 3 or len(raw_purpose) > 150:
        return jsonify({
            "success": False,
            "error": "Please specify the purpose of the meeting (3–150 characters).",
            "field": "purpose"
        }), 400

    # 4. Meeting Date validation (must not be past date)
    if not raw_date:
        return jsonify({
            "success": False,
            "error": "Meeting date is required.",
            "field": "meeting_date"
        }), 400

    try:
        parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        today = date.today()
        if parsed_date < today:
            return jsonify({
                "success": False,
                "error": "Meeting date cannot be in the past. Please select today or a future date.",
                "field": "meeting_date"
            }), 400
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid date format. Use YYYY-MM-DD.",
            "field": "meeting_date"
        }), 400

    # 5. Meeting Time Slot validation
    if not raw_time or len(raw_time) < 3:
        return jsonify({
            "success": False,
            "error": "Please select a preferred time slot.",
            "field": "meeting_time"
        }), 400

    # 6. Check for duplicate booking
    existing = MeetingBooking.check_duplicate(raw_email, raw_date, raw_time)
    if existing:
        return jsonify({
            "success": False,
            "error": "You already have an active meeting request for this date and time slot. Please choose another slot or await confirmation.",
            "existing_booking_id": existing["id"]
        }), 409

    # Sanitize inputs
    full_name = html.escape(raw_name)
    email = html.escape(raw_email)
    purpose = html.escape(raw_purpose)
    meeting_date = html.escape(raw_date)
    meeting_time = html.escape(raw_time)
    notes = html.escape(raw_notes)

    try:
        booking_id = MeetingBooking.create(
            full_name=full_name,
            email=email,
            purpose=purpose,
            meeting_date=meeting_date,
            meeting_time=meeting_time,
            notes=notes
        )

        booking_record = {
            "id": booking_id,
            "full_name": full_name,
            "email": email,
            "purpose": purpose,
            "meeting_date": meeting_date,
            "meeting_time": meeting_time,
            "notes": notes,
            "status": "Pending"
        }

        # Dispatch email notification to Sahil
        email_result = email_service.send_meeting_notification(booking_record)

        return jsonify({
            "success": True,
            "message": f"Thank you, {raw_name}! Your Google Meet request for {meeting_date} at {meeting_time} has been received. Sahil will review and email you the Google Meet link shortly.",
            "booking_id": booking_id,
            "booking": booking_record,
            "email_notification": email_result
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to record meeting request due to a database error.",
            "details": str(e)
        }), 500


@api_bp.route("/meetings/status/<int:booking_id>", methods=["GET"])
def get_meeting_status(booking_id):
    """Retrieve status and Google Meet link for a scheduled meeting."""
    try:
        booking = MeetingBooking.get_by_id(booking_id)
        if not booking:
            return jsonify({
                "success": False,
                "error": "Meeting booking not found."
            }), 404

        return jsonify({
            "success": True,
            "booking": {
                "id": booking["id"],
                "full_name": booking["full_name"],
                "email": booking["email"],
                "purpose": booking["purpose"],
                "meeting_date": booking["meeting_date"],
                "meeting_time": booking["meeting_time"],
                "status": booking["status"],
                "google_meet_link": booking.get("google_meet_link", ""),
                "created_at": booking["created_at"]
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/meetings/<int:booking_id>/action", methods=["POST"])
def update_meeting_action(booking_id):
    """
    Approve or reject a meeting booking.
    When approving, attaches a Google Meet link and sends confirmation to visitor.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    action = (data.get("action") or data.get("status") or "").strip().capitalize()
    custom_link = str(data.get("google_meet_link") or "").strip()
    notes = str(data.get("notes") or "").strip()

    if action not in ["Approved", "Rejected"]:
        return jsonify({
            "success": False,
            "error": "Invalid action. Must be 'Approved' or 'Rejected'."
        }), 400

    booking = MeetingBooking.get_by_id(booking_id)
    if not booking:
        return jsonify({
            "success": False,
            "error": "Meeting booking not found."
        }), 404

    # Default Google Meet link format if not specified
    if action == "Approved" and not custom_link:
        # Standard clean meet URL pattern for Sahil's sessions
        custom_link = f"https://meet.google.com/shn-wzpk-{booking_id:03d}"

    updated = MeetingBooking.update_status(
        booking_id=booking_id,
        status=action,
        google_meet_link=custom_link if action == "Approved" else "",
        notes=notes
    )

    if not updated:
        return jsonify({
            "success": False,
            "error": "Failed to update meeting status."
        }), 500

    updated_booking = MeetingBooking.get_by_id(booking_id)

    # Send confirmation email to visitor
    email_result = email_service.send_booking_confirmation_to_visitor(updated_booking)

    return jsonify({
        "success": True,
        "message": f"Meeting #{booking_id} marked as {action}.",
        "booking": updated_booking,
        "visitor_email_result": email_result
    }), 200


@api_bp.route("/meetings", methods=["GET"])
def list_meetings():
    """Retrieve all meeting bookings."""
    try:
        bookings = MeetingBooking.get_all()
        return jsonify({
            "success": True,
            "count": len(bookings),
            "meetings": bookings
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

