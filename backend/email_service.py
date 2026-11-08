"""
Sahil Nawaz Portfolio — Email Notification Service
Handles automated notifications for contact inquiries and Google Meet scheduling requests.
Uses standard library smtplib with TLS encryption and graceful fallback when credentials are not configured.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Dynamic Configuration from Environment Variables
def get_smtp_credentials():
    """
    Dynamically read SMTP credentials and clean formatting.
    Supports GMAIL_APP_PASSWORD, SMTP_PASS, SMTP_PASSWORD with or without spaces.
    """
    server = os.environ.get("SMTP_SERVER") or os.environ.get("SMTP_HOST") or "smtp.gmail.com"
    try:
        port = int(os.environ.get("SMTP_PORT", 587))
    except (ValueError, TypeError):
        port = 587
    notification_email = os.environ.get("NOTIFICATION_EMAIL") or "sahilnawaaz257@gmail.com"
    username = (
        os.environ.get("SMTP_USERNAME")
        or os.environ.get("SMTP_USER")
        or os.environ.get("GMAIL_USER")
        or notification_email
    )
    raw_pass = (
        os.environ.get("SMTP_PASSWORD")
        or os.environ.get("SMTP_PASS")
        or os.environ.get("GMAIL_APP_PASSWORD")
        or ""
    )
    # Strip spaces often present in Google App Passwords (e.g., 'abcd efgh ijkl mnop')
    password = str(raw_pass).replace(" ", "").replace("-", "").strip()
    return server, port, username, password, notification_email

def is_smtp_configured():
    """Check if SMTP credentials are provided and meet minimum length."""
    _, _, username, password, _ = get_smtp_credentials()
    return bool(username and password and len(password) >= 8)

def _dispatch_email(to_email, subject, text_content, html_content=None):
    """
    Internal helper to send an email via SMTP.
    Uses UTF-8 encoding for reliable unicode/emoji transmission.
    Returns dict with delivery status.
    """
    server_host, server_port, username, password, _ = get_smtp_credentials()

    if not is_smtp_configured():
        # Clean local logging when SMTP is not configured
        print(f"[EMAIL SERVICE - SIMULATED] To: {to_email} | Subject: {subject}")
        print(f"Content Summary: {text_content[:200]}...")
        return {
            "success": False,
            "configured": False,
            "simulated": True,
            "message": "SMTP credentials not configured. Notification recorded locally in database."
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Sahil Nawaz Portfolio <{username}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Reply-To"] = username

        part_text = MIMEText(text_content, "plain", "utf-8")
        msg.attach(part_text)

        if html_content:
            part_html = MIMEText(html_content, "html", "utf-8")
            msg.attach(part_html)

        server = smtplib.SMTP(server_host, server_port, timeout=12.0)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(username, password)
        server.sendmail(username, [to_email], msg.as_string())
        server.quit()

        print(f"[EMAIL SERVICE - DELIVERED] Email successfully sent to {to_email} | Subject: {subject}")
        return {
            "success": True,
            "configured": True,
            "simulated": False,
            "message": f"Email successfully dispatched to {to_email}"
        }
    except Exception as e:
        print(f"[EMAIL SERVICE ERROR] Failed to send email to {to_email}: {e}")
        return {
            "success": False,
            "configured": True,
            "simulated": False,
            "error": str(e),
            "message": f"Failed to send email due to SMTP transport error: {e}"
        }

def send_contact_notification(name, email, subject, message):
    """Notify Sahil when a visitor submits a contact message."""
    email_subj = f"New Contact Inquiry: {name} — {subject}"
    text_body = (
        f"You have received a new message from your portfolio website!\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Subject: {subject}\n\n"
        f"Message:\n{message}\n\n"
        f"You can reply directly to: {email}\n"
        f"— Sahil Nawaz Portfolio Notification Engine"
    )
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #39312e; max-width: 600px; padding: 20px; border: 1px solid #f3b5aa; border-radius: 8px;">
        <h2 style="color: #df7568; margin-top: 0;">New Contact Inquiry</h2>
        <p><strong>From:</strong> {name} (&lt;<a href="mailto:{email}">{email}</a>&gt;)</p>
        <p><strong>Subject:</strong> {subject}</p>
        <div style="background: #fff5f3; padding: 15px; border-radius: 6px; border-left: 4px solid #df7568; margin: 20px 0;">
            <p style="margin: 0; white-space: pre-wrap;">{message}</p>
        </div>
        <p style="font-size: 13px; color: #7a6e69;">Reply directly to <a href="mailto:{email}">{email}</a></p>
    </div>
    """
    _, _, _, _, notif_email = get_smtp_credentials()
    return _dispatch_email(notif_email, email_subj, text_body, html_body)

def send_contact_confirmation_to_visitor(name, email, subject, message):
    """Send an automated confirmation receipt to the visitor."""
    email_subj = f"Message Received: Thank you for contacting Sahil Nawaz — {subject}"
    text_body = (
        f"Hi {name},\n\n"
        f"Thank you for reaching out through my portfolio website!\n\n"
        f"I have received your message regarding: \"{subject}\".\n"
        f"I will review your inquiry and get back to you shortly.\n\n"
        f"Your message copy:\n"
        f"{message}\n\n"
        f"Best regards,\n"
        f"Sahil Nawaz\n"
        f"Forward Deployed Developer\n"
        f"https://github.com/sahilnawaz257"
    )
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #39312e; max-width: 600px; padding: 24px; border: 1px solid #f3b5aa; border-radius: 10px; background: #ffffff;">
        <h2 style="color: #df7568; margin-top: 0;">Thank You for Reaching Out!</h2>
        <p>Hi {name},</p>
        <p>I have received your message regarding <strong>"{subject}"</strong> and will get back to you as soon as possible.</p>
        <div style="background: #fff5f3; padding: 16px; border-radius: 8px; border-left: 4px solid #df7568; margin: 20px 0;">
            <p style="margin: 0 0 8px 0; font-size: 12px; color: #7a6e69; text-transform: uppercase; font-weight: bold;">Your Message:</p>
            <p style="margin: 0; white-space: pre-wrap; color: #201a19;">{message}</p>
        </div>
        <p style="margin-top: 24px; font-size: 14px; color: #53433f;">
            Best regards,<br>
            <strong>Sahil Nawaz</strong><br>
            <span style="color: #df7568; font-size: 13px;">Forward Deployed Developer</span>
        </p>
    </div>
    """
    return _dispatch_email(email, email_subj, text_body, html_body)

def dispatch_contact_emails(name, email, subject, message):
    """
    Dispatch owner alert (to sahilnawaz257@gmail.com) and visitor confirmation receipt.
    Tracks delivery status for each recipient separately.
    Returns summary dict with granular delivery states.
    """
    owner_res = send_contact_notification(name, email, subject, message)
    visitor_res = send_contact_confirmation_to_visitor(name, email, subject, message)

    owner_ok = bool(owner_res and owner_res.get("success"))
    visitor_ok = bool(visitor_res and visitor_res.get("success"))

    if not is_smtp_configured():
        overall_status = "unconfigured"
    elif owner_ok and visitor_ok:
        overall_status = "delivered"
    elif owner_ok or visitor_ok:
        overall_status = "partial"
    else:
        overall_status = "failed"

    return {
        "status": overall_status,
        "owner_notified": owner_ok,
        "owner_details": owner_res,
        "visitor_confirmed": visitor_ok,
        "visitor_details": visitor_res
    }

import hmac
import hashlib

def generate_booking_token(booking_id, action, secret_key):
    """Generate a tamper-proof cryptographic token for one-click email approval."""
    payload = f"meet:{booking_id}:{action}".encode("utf-8")
    key = str(secret_key or "sahil-meet-secure-key").encode("utf-8")
    return hmac.new(key, payload, hashlib.sha256).hexdigest()

def verify_booking_token(booking_id, action, token, secret_key):
    """Verify HMAC token authenticity."""
    expected = generate_booking_token(booking_id, action, secret_key)
    return hmac.compare_digest(str(expected), str(token or ""))

def send_meeting_notification(booking, base_url="", secret_key=""):
    """
    Notify Sahil when a new meeting is requested.
    Includes booking reference, status, and HMAC-signed approval/rejection links.
    """
    booking_id = booking.get("id")
    name = booking.get("full_name")
    email = booking.get("email")
    purpose = booking.get("purpose")
    date = booking.get("meeting_date") or booking.get("preferred_date")
    time_slot = booking.get("meeting_time") or booking.get("preferred_time")
    status = booking.get("status", "Pending")
    notes = booking.get("notes") or "None provided"

    # Generate one-click action links if base_url is available
    action_html = ""
    action_text = ""
    if base_url and secret_key and booking_id:
        approve_token = generate_booking_token(booking_id, "approve", secret_key)
        reject_token = generate_booking_token(booking_id, "reject", secret_key)
        approve_url = f"{base_url}/api/meetings/action?id={booking_id}&action=approve&token={approve_token}"
        reject_url = f"{base_url}/api/meetings/action?id={booking_id}&action=reject&token={reject_token}"

        action_text = (
            f"\n--- OWNER QUICK ACTIONS ---\n"
            f"Approve & Confirm Meeting: {approve_url}\n"
            f"Reject Request: {reject_url}\n"
        )
        action_html = f"""
        <div style="margin: 24px 0 10px 0; padding: 18px; background: #fff8f7; border: 1px solid #f3b5aa; border-radius: 8px;">
            <p style="margin: 0 0 12px 0; font-size: 13px; font-weight: bold; color: #53433f; text-transform: uppercase;">Owner Quick Actions:</p>
            <div style="display: flex; gap: 12px;">
                <a href="{approve_url}" style="background: #22c55e; color: #ffffff; text-decoration: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; display: inline-block;">✓ Approve Meeting</a>
                &nbsp;&nbsp;
                <a href="{reject_url}" style="background: #ef4444; color: #ffffff; text-decoration: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; display: inline-block;">✕ Decline</a>
            </div>
            <p style="margin: 10px 0 0 0; font-size: 11px; color: #7a6e69;">Clicking Approve automatically generates/attaches a Google Meet link and confirms the visitor.</p>
        </div>
        """

    email_subj = f"New Google Meet Request: {name} — Ref #{str(booking_id)[:8]} ({date} @ {time_slot})"
    text_body = (
        f"New Google Meet scheduling request received!\n\n"
        f"Booking Reference: #{booking_id}\n"
        f"Visitor Name: {name}\n"
        f"Email: {email}\n"
        f"Purpose: {purpose}\n"
        f"Preferred Date: {date}\n"
        f"Preferred Time: {time_slot}\n"
        f"Status: {status}\n"
        f"Notes / Agenda: {notes}\n"
        f"{action_text}\n"
        f"— Sahil Nawaz Portfolio Scheduling Engine"
    )
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #39312e; max-width: 620px; padding: 24px; border: 1px solid #f3b5aa; border-radius: 10px; background: #ffffff;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #fceae7; padding-bottom: 12px; margin-bottom: 16px;">
            <h2 style="color: #df7568; margin: 0; font-size: 20px;">📅 New Google Meet Request</h2>
            <span style="background: #fff0ed; color: #df7568; font-family: monospace; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold;">Ref: #{str(booking_id)[:8]}</span>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
            <tr><td style="padding: 6px 0; color: #7a6e69; width: 140px;"><strong>Visitor Name:</strong></td><td><strong>{name}</strong></td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Email Address:</strong></td><td><a href="mailto:{email}">{email}</a></td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Meeting Topic:</strong></td><td>{purpose}</td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Preferred Date:</strong></td><td>{date}</td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Preferred Time:</strong></td><td>{time_slot}</td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Booking Status:</strong></td><td><span style="background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">{status}</span></td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Agenda / Notes:</strong></td><td>{notes}</td></tr>
        </table>
        {action_html}
        <p style="font-size: 12px; color: #8e807a; margin-top: 20px; border-top: 1px solid #f5ebe8; padding-top: 10px;">
            This email was generated securely by your portfolio backend. Never forward action links publicly.
        </p>
    </div>
    """
    _, _, _, _, notif_email = get_smtp_credentials()
    return _dispatch_email(notif_email, email_subj, text_body, html_body)

def send_booking_receipt_to_visitor(booking):
    """Send an immediate acknowledgement receipt to the visitor with their booking details."""
    to_email = booking.get("email")
    booking_id = booking.get("id")
    name = booking.get("full_name")
    purpose = booking.get("purpose")
    date = booking.get("meeting_date") or booking.get("preferred_date")
    time_slot = booking.get("meeting_time") or booking.get("preferred_time")

    email_subj = f"Google Meet Request Received: Sahil Nawaz — Ref #{str(booking_id)[:8]}"
    text_body = (
        f"Hi {name},\n\n"
        f"Thank you for requesting a Google Meet session with Sahil Nawaz!\n\n"
        f"Booking Reference: #{booking_id}\n"
        f"Topic / Purpose: {purpose}\n"
        f"Requested Date: {date}\n"
        f"Requested Time Slot: {time_slot}\n"
        f"Status: Pending Review\n\n"
        f"Sahil has been notified and will review your request shortly.\n"
        f"Once approved, you will receive an official confirmation email containing the Google Meet link.\n\n"
        f"Best regards,\n"
        f"Sahil Nawaz — Forward Deployed Developer\n"
        f"https://github.com/sahilnawaz257"
    )
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #39312e; max-width: 600px; padding: 24px; border: 1px solid #f3b5aa; border-radius: 10px; background: #ffffff;">
        <h2 style="color: #df7568; margin-top: 0;">📅 Meeting Request Received</h2>
        <p>Hi {name},</p>
        <p>Thank you for requesting a Google Meet consultation. Your scheduling request has been securely recorded.</p>
        <div style="background: #fff8f7; padding: 18px; border-radius: 8px; border-left: 4px solid #df7568; margin: 20px 0;">
            <p style="margin: 0 0 6px 0;"><strong>Reference ID:</strong> <span style="font-family: monospace; color: #df7568;">#{str(booking_id)[:8]}</span></p>
            <p style="margin: 0 0 6px 0;"><strong>Date:</strong> {date}</p>
            <p style="margin: 0 0 6px 0;"><strong>Time Slot:</strong> {time_slot}</p>
            <p style="margin: 0 0 6px 0;"><strong>Discussion Topic:</strong> {purpose}</p>
            <p style="margin: 0;"><strong>Status:</strong> <span style="background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">Pending Review</span></p>
        </div>
        <p style="font-size: 14px; color: #53433f;">
            Sahil will review your request and send a confirmation email with the official Google Meet link to this address shortly.
        </p>
        <p style="margin-top: 24px; font-size: 14px; color: #53433f;">
            Best regards,<br>
            <strong>Sahil Nawaz</strong><br>
            <span style="color: #df7568; font-size: 13px;">Forward Deployed Developer</span>
        </p>
    </div>
    """
    return _dispatch_email(to_email, email_subj, text_body, html_body)

def dispatch_meeting_booking_emails(booking, base_url="", secret_key=""):
    """
    Dispatch both owner alert (with one-click HMAC action links) and visitor receipt.
    Tracks delivery state for both recipients separately.
    """
    owner_res = send_meeting_notification(booking, base_url=base_url, secret_key=secret_key)
    visitor_res = send_booking_receipt_to_visitor(booking)

    owner_ok = bool(owner_res and owner_res.get("success"))
    visitor_ok = bool(visitor_res and visitor_res.get("success"))

    if not is_smtp_configured():
        overall_status = "unconfigured"
    elif owner_ok and visitor_ok:
        overall_status = "delivered"
    elif owner_ok or visitor_ok:
        overall_status = "partial"
    else:
        overall_status = "failed"

    return {
        "status": overall_status,
        "owner_notified": owner_ok,
        "owner_details": owner_res,
        "visitor_confirmed": visitor_ok,
        "visitor_details": visitor_res
    }

def send_booking_confirmation_to_visitor(booking):
    """Notify visitor with meeting status and Google Meet link."""
    to_email = booking.get("email")
    name = booking.get("full_name")
    date = booking.get("meeting_date")
    time_slot = booking.get("meeting_time")
    status = booking.get("status")
    meet_link = booking.get("google_meet_link") or ""

    _, _, _, _, notif_email = get_smtp_credentials()
    if status == "Approved":
        email_subj = f"Confirmed: Google Meet with Sahil Nawaz on {date}"
        text_body = (
            f"Hi {name},\n\n"
            f"Your Google Meet session with Sahil Nawaz has been confirmed!\n\n"
            f"Date: {date}\n"
            f"Time Slot: {time_slot}\n"
            f"Google Meet Link: {meet_link}\n\n"
            f"Looking forward to connecting with you!\n"
            f"Best regards,\nSahil Nawaz — Forward Deployed Developer"
        )
        html_body = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #39312e; max-width: 600px; padding: 20px; border: 1px solid #f3b5aa; border-radius: 8px;">
            <h2 style="color: #df7568; margin-top: 0;">🎉 Meeting Confirmed!</h2>
            <p>Hi {name},</p>
            <p>Your Google Meet session with Sahil Nawaz has been approved and scheduled.</p>
            <div style="background: #fff5f3; padding: 15px; border-radius: 6px; margin: 15px 0;">
                <p><strong>Date:</strong> {date}</p>
                <p><strong>Time Slot:</strong> {time_slot}</p>
                <p><strong>Google Meet Link:</strong> <a href="{meet_link}" target="_blank" style="color: #df7568; font-weight: bold;">{meet_link}</a></p>
            </div>
            <p>See you then!</p>
            <p>Best regards,<br><strong>Sahil Nawaz</strong><br>Forward Deployed Developer</p>
        </div>
        """
    else:
        email_subj = f"Update on your meeting request with Sahil Nawaz"
        text_body = (
            f"Hi {name},\n\n"
            f"Thank you for reaching out to schedule a meeting for {date} at {time_slot}.\n"
            f"Unfortunately, this slot cannot be accommodated at this time ({status}).\n\n"
            f"Please feel free to reach out directly via email at {notif_email} or choose an alternate time.\n\n"
            f"Best regards,\nSahil Nawaz"
        )
        html_body = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #39312e; max-width: 600px; padding: 20px; border: 1px solid #f3b5aa; border-radius: 8px;">
            <h2 style="color: #df7568; margin-top: 0;">Meeting Request Update</h2>
            <p>Hi {name},</p>
            <p>Thank you for reaching out to schedule a meeting for <strong>{date}</strong> at <strong>{time_slot}</strong>.</p>
            <p>Unfortunately, this slot is not available or could not be accommodated (Status: {status}).</p>
            <p>Please feel free to reply directly or contact Sahil at <a href="mailto:{notif_email}">{notif_email}</a> to reschedule.</p>
            <p>Best regards,<br><strong>Sahil Nawaz</strong></p>
        </div>
        """

    return _dispatch_email(to_email, email_subj, text_body, html_body)

