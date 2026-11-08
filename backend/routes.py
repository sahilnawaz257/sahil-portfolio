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
from models import ContactMessage, Project, MeetingBooking, Education, Experience, Skill
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


@api_bp.route("/supabase/status", methods=["GET"])
def supabase_status():
    """
    Supabase Python SDK connection health and engine mode status.
    Exposes operational status without exposing private keys.
    """
    try:
        import supabase_client
        status_info = supabase_client.check_supabase_connection()
        return jsonify({
            "success": True,
            "supabase": status_info
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


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


@api_bp.route("/projects/<project_id>", methods=["GET"])
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


@api_bp.route("/education", methods=["GET"])
def list_education():
    """Retrieve formal education records."""
    try:
        education = Education.get_all()
        return jsonify({
            "success": True,
            "count": len(education),
            "education": education
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve education records.",
            "details": str(e)
        }), 500


@api_bp.route("/experience", methods=["GET"])
def list_experience():
    """Retrieve professional experience records."""
    try:
        experience = Experience.get_all()
        return jsonify({
            "success": True,
            "count": len(experience),
            "experience": experience
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve experience records.",
            "details": str(e)
        }), 500


@api_bp.route("/skills", methods=["GET"])
def list_skills():
    """Retrieve technical and product/business skills."""
    try:
        skills = Skill.get_all()
        grouped = Skill.get_grouped()
        return jsonify({
            "success": True,
            "count": len(skills),
            "skills": skills,
            "categories": grouped
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to retrieve skills.",
            "details": str(e)
        }), 500


@api_bp.route("/contact", methods=["POST"])
def submit_contact():
    """
    Accept, validate, sanitize, and store contact form submissions into SQLite.
    Protected with sliding-window rate limiting and strict server-side validation.
    """
    # Rate limit check: Max 25 submissions per minute per IP
    client_ip = get_client_ip()
    if not check_rate_limit(f"contact:{client_ip}", limit=25, window=60):
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

    # Check for rapid duplicate submission (spam / accidental double submit prevention)
    duplicate_msg = ContactMessage.check_duplicate(email=raw_email, message=raw_message, window_seconds=60)
    if duplicate_msg:
        return jsonify({
            "success": False,
            "error": "Duplicate submission detected. Your message has already been received. Please wait before sending again.",
            "duplicate": True,
            "field": "message"
        }), 429

    # Sanitize inputs to prevent stored XSS attacks
    full_name = html.escape(raw_name)
    email = html.escape(raw_email)
    subject = html.escape(raw_subject) if raw_subject else "Forward Deployed Opportunity / Project Collaboration"
    message = html.escape(raw_message)

    # Save to Supabase PostgreSQL (or fallback SQLite engine)
    try:
        msg_id = ContactMessage.create(
            full_name=full_name,
            email=email,
            subject=subject,
            message=message
        )
    except Exception as db_err:
        # Safe logging without exposing DB credentials
        return jsonify({
            "success": False,
            "error": "Database error while recording your message. Please try again or email directly to sahilnawaaz257@gmail.com."
        }), 500

    # Dispatch Email Notifications (Owner alert to sahilnawaz257@gmail.com + Visitor confirmation receipt)
    try:
        email_result = email_service.dispatch_contact_emails(
            name=raw_name,
            email=raw_email,
            subject=raw_subject or "Portfolio Inquiry",
            message=raw_message
        )
    except Exception as email_err:
        email_result = {
            "status": "failed",
            "owner_notified": False,
            "visitor_confirmed": False,
            "error": "Notification dispatch encountered an internal transport error."
        }

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


# ==============================================================================
# Google Meet Scheduling APIs
# ==============================================================================

STANDARD_MEETING_SLOTS = [
    "10:00 AM - 10:30 AM",
    "11:30 AM - 12:00 PM",
    "02:00 PM - 02:30 PM",
    "04:30 PM - 05:00 PM",
    "07:00 PM - 07:30 PM"
]

@api_bp.route("/meetings/available-slots", methods=["GET"])
def get_available_slots():
    """
    Retrieve genuinely available time slots for a specified date.
    Cross-checks existing non-rejected reservations in meeting_bookings.
    """
    raw_date = request.args.get("date", "").strip()
    if not raw_date:
        raw_date = date.today().isoformat()

    try:
        parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        if parsed_date < date.today():
            return jsonify({
                "success": False,
                "error": "Selected date is in the past. Please choose today or a future date.",
                "date": raw_date,
                "slots": []
            }), 400
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid date format. Expected YYYY-MM-DD.",
            "date": raw_date,
            "slots": []
        }), 400

    booked_slots = MeetingBooking.get_booked_slots(raw_date)
    slots_status = []
    for s in STANDARD_MEETING_SLOTS:
        # Check if slot is already reserved
        is_booked = any(
            s.lower() in str(b).lower() or str(b).lower() in s.lower()
            for b in booked_slots
        )
        slots_status.append({
            "slot": s,
            "available": not is_booked
        })

    return jsonify({
        "success": True,
        "date": raw_date,
        "slots": slots_status,
        "available_count": sum(1 for s in slots_status if s["available"])
    }), 200


@api_bp.route("/meetings/book", methods=["POST"])
@api_bp.route("/meetings/request", methods=["POST"])
def book_meeting():
    """
    Schedule a Google Meet appointment.
    Validates name, email, purpose, future date, and time slot.
    Checks for duplicate requests, slot availability, and dispatches notifications.
    """
    from flask import current_app

    client_ip = get_client_ip()
    if not check_rate_limit(f"meeting:{client_ip}", limit=25, window=60):
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
    raw_date = str(data.get("preferred_date") or data.get("meeting_date") or data.get("date") or "").strip()
    raw_time = str(data.get("preferred_time") or data.get("meeting_time") or data.get("time") or "").strip()
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

    # 6. Check for duplicate booking by this email
    existing_user_booking = MeetingBooking.check_duplicate(raw_email, raw_date, raw_time)
    if existing_user_booking:
        return jsonify({
            "success": False,
            "error": "You already have an active meeting request for this date and time slot. Please choose another slot or await confirmation.",
            "existing_booking_id": existing_user_booking["id"],
            "field": "meeting_time"
        }), 409

    # 7. Check if this time slot is already taken on this date by any user
    booked_slots = MeetingBooking.get_booked_slots(raw_date)
    is_slot_taken = any(
        raw_time.lower() in str(b).lower() or str(b).lower() in raw_time.lower()
        for b in booked_slots
    )
    if is_slot_taken:
        return jsonify({
            "success": False,
            "error": f"The time slot '{raw_time}' has already been booked for {raw_date}. Please select another available time slot.",
            "field": "meeting_time",
            "conflict": True
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
            preferred_date=meeting_date,
            preferred_time=meeting_time,
            notes=notes
        )

        booking_record = {
            "id": booking_id,
            "full_name": full_name,
            "email": email,
            "purpose": purpose,
            "preferred_date": meeting_date,
            "preferred_time": meeting_time,
            "meeting_date": meeting_date,
            "meeting_time": meeting_time,
            "meeting_link": "",
            "notes": notes,
            "status": "Pending",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        # Dispatch email notification to Sahil (with signed HMAC approval link) + receipt to visitor
        base_url = request.host_url.rstrip("/")
        secret_key = current_app.config.get("SECRET_KEY", "sahil-meet-secure-key")
        email_result = email_service.dispatch_meeting_booking_emails(
            booking=booking_record,
            base_url=base_url,
            secret_key=secret_key
        )

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
            "error": "Failed to record meeting request due to a database error. Please try again.",
            "details": str(e)
        }), 500


@api_bp.route("/meetings/action", methods=["GET", "POST"])
def handle_meeting_action():
    """
    Secure owner-controlled approval/rejection endpoint.
    Protected with HMAC cryptographic signature; zero admin login needed.
    """
    from flask import current_app, render_template_string
    import google_calendar

    data = request.get_json(silent=True) or request.args.to_dict()
    booking_id = data.get("id")
    action = str(data.get("action", "")).lower()
    token = data.get("token")
    custom_link = str(data.get("link", "")).strip()

    if not booking_id or action not in ("approve", "reject"):
        return jsonify({"success": False, "error": "Invalid action parameters."}), 400

    secret_key = current_app.config.get("SECRET_KEY", "sahil-meet-secure-key")
    if not email_service.verify_booking_token(booking_id, action, token, secret_key):
        return jsonify({"success": False, "error": "Unauthorized or invalid action token."}), 403

    booking = MeetingBooking.get_by_id(booking_id)
    if not booking:
        return jsonify({"success": False, "error": "Booking record not found."}), 404

    if action == "approve":
        meet_link = custom_link
        # If no link provided and Google Calendar credentials exist, generate genuine Meet link
        if not meet_link and google_calendar.is_google_calendar_configured():
            cal_res = google_calendar.create_google_meet_event(
                summary=f"Google Meet: {booking['full_name']} — {booking['purpose']}",
                description=f"Consultation scheduled with Sahil Nawaz.\nNotes: {booking.get('notes', '')}",
                attendee_email=booking["email"],
                date_str=booking["meeting_date"],
                time_slot_str=booking["meeting_time"]
            )
            if cal_res.get("success"):
                meet_link = cal_res.get("meeting_link")

        updated = MeetingBooking.update_status(booking_id, "Approved", meeting_link=meet_link)
        email_service.send_booking_confirmation_to_visitor(updated)
        status_msg = f"Meeting #{str(booking_id)[:8]} has been Approved!"
    else:
        updated = MeetingBooking.update_status(booking_id, "Rejected")
        email_service.send_booking_confirmation_to_visitor(updated)
        status_msg = f"Meeting #{str(booking_id)[:8]} has been Declined."

    # Return JSON for API clients
    if request.headers.get("Accept") == "application/json" or request.is_json:
        return jsonify({
            "success": True,
            "message": status_msg,
            "booking": updated
        }), 200

    # Return styled HTML confirmation for email clicks
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Booking Action — Sahil Nawaz Portfolio</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #fff5f3; color: #201a19; padding: 40px 20px; display: flex; justify-content: center; }
            .card { background: #ffffff; max-width: 540px; width: 100%; border: 1px solid #f3b5aa; border-radius: 12px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
            h2 { color: #df7568; margin-top: 0; }
            .badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 13px; }
            .badge-approved { background: #dcfce7; color: #15803d; }
            .badge-rejected { background: #fee2e2; color: #b91c1c; }
            .row { margin: 12px 0; }
            .label { color: #7a6e69; font-size: 12px; text-transform: uppercase; font-weight: bold; }
            .val { font-size: 15px; margin-top: 3px; }
            .link-box { background: #fff0ed; padding: 12px; border-radius: 6px; word-break: break-all; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>{{ status_msg }}</h2>
            <div class="row">
                <div class="label">Visitor:</div>
                <div class="val">{{ booking.full_name }} ({{ booking.email }})</div>
            </div>
            <div class="row">
                <div class="label">Date & Time:</div>
                <div class="val">{{ booking.meeting_date }} @ {{ booking.meeting_time }}</div>
            </div>
            <div class="row">
                <div class="label">Purpose:</div>
                <div class="val">{{ booking.purpose }}</div>
            </div>
            <div class="row">
                <div class="label">Status:</div>
                <div class="val"><span class="badge {{ 'badge-approved' if booking.status == 'Approved' else 'badge-rejected' }}">{{ booking.status }}</span></div>
            </div>
            {% if booking.meeting_link or booking.google_meet_link %}
            <div class="link-box">
                <strong>Google Meet Link:</strong><br>
                <a href="{{ booking.meeting_link or booking.google_meet_link }}" target="_blank">{{ booking.meeting_link or booking.google_meet_link }}</a>
            </div>
            {% endif %}
            <p style="color: #7a6e69; font-size: 13px; margin-top: 24px;">An automated confirmation update has been dispatched to {{ booking.email }}.</p>
        </div>
    </body>
    </html>
    """, status_msg=status_msg, booking=updated), 200


@api_bp.route("/meetings/status/<booking_id>", methods=["GET"])
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
                "created_at": booking.get("created_at")
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

