"""
Sahil Nawaz Portfolio — Email Notification Service
Handles automated notifications for contact inquiries and Google Meet scheduling requests.
Uses standard library smtplib with TLS encryption and graceful fallback when credentials are not configured.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration from Environment Variables
SMTP_SERVER = os.environ.get("SMTP_SERVER") or os.environ.get("SMTP_HOST") or "smtp.gmail.com"
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME") or os.environ.get("SMTP_USER") or ""
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD") or os.environ.get("SMTP_PASS") or ""
NOTIFICATION_EMAIL = os.environ.get("NOTIFICATION_EMAIL") or "sahilnawaz257@gmail.com"

def is_smtp_configured():
    """Check if SMTP credentials are provided."""
    return bool(SMTP_USERNAME and SMTP_PASSWORD)

def _dispatch_email(to_email, subject, text_content, html_content=None):
    """
    Internal helper to send an email via SMTP.
    Returns dict with delivery status.
    """
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
        msg["From"] = f"Sahil Nawaz Portfolio <{SMTP_USERNAME}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        part_text = MIMEText(text_content, "plain")
        msg.attach(part_text)

        if html_content:
            part_html = MIMEText(html_content, "html")
            msg.attach(part_html)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10.0)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, [to_email], msg.as_string())
        server.quit()

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
            "message": "Failed to send email due to SMTP transport error."
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
    return _dispatch_email(NOTIFICATION_EMAIL, email_subj, text_body, html_body)

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

def send_meeting_notification(booking):
    """Notify Sahil when a new meeting is requested."""
    name = booking.get("full_name")
    email = booking.get("email")
    purpose = booking.get("purpose")
    date = booking.get("meeting_date")
    time_slot = booking.get("meeting_time")
    notes = booking.get("notes") or "None provided"

    email_subj = f"New Google Meet Request: {name} ({date} @ {time_slot})"
    text_body = (
        f"New Google Meet scheduling request received!\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Purpose: {purpose}\n"
        f"Requested Date: {date}\n"
        f"Requested Time Slot: {time_slot}\n"
        f"Notes / Agenda: {notes}\n\n"
        f"Status: Pending\n"
        f"— Sahil Nawaz Portfolio Scheduling System"
    )
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #39312e; max-width: 600px; padding: 20px; border: 1px solid #f3b5aa; border-radius: 8px;">
        <h2 style="color: #df7568; margin-top: 0;">📅 New Google Meet Request</h2>
        <p>A visitor has requested a meeting on your portfolio.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Full Name:</strong></td><td>{name}</td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Email:</strong></td><td><a href="mailto:{email}">{email}</a></td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Purpose:</strong></td><td>{purpose}</td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Date:</strong></td><td>{date}</td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Time Slot:</strong></td><td>{time_slot}</td></tr>
            <tr><td style="padding: 6px 0; color: #7a6e69;"><strong>Agenda / Notes:</strong></td><td>{notes}</td></tr>
        </table>
        <p style="font-size: 13px; color: #7a6e69;">Status is currently <strong>Pending</strong>. You can approve and generate a Google Meet link from your system.</p>
    </div>
    """
    return _dispatch_email(NOTIFICATION_EMAIL, email_subj, text_body, html_body)

def send_booking_confirmation_to_visitor(booking):
    """Notify visitor with meeting status and Google Meet link."""
    to_email = booking.get("email")
    name = booking.get("full_name")
    date = booking.get("meeting_date")
    time_slot = booking.get("meeting_time")
    status = booking.get("status")
    meet_link = booking.get("google_meet_link") or ""

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
            f"Please feel free to reach out directly via email at {NOTIFICATION_EMAIL} or choose an alternate time.\n\n"
            f"Best regards,\nSahil Nawaz"
        )
        html_body = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #39312e; max-width: 600px; padding: 20px; border: 1px solid #f3b5aa; border-radius: 8px;">
            <h2 style="color: #df7568; margin-top: 0;">Meeting Request Update</h2>
            <p>Hi {name},</p>
            <p>Thank you for reaching out to schedule a meeting for <strong>{date}</strong> at <strong>{time_slot}</strong>.</p>
            <p>Unfortunately, this slot is not available or could not be accommodated (Status: {status}).</p>
            <p>Please feel free to reply directly or contact Sahil at <a href="mailto:{NOTIFICATION_EMAIL}">{NOTIFICATION_EMAIL}</a> to reschedule.</p>
            <p>Best regards,<br><strong>Sahil Nawaz</strong></p>
        </div>
        """

    return _dispatch_email(to_email, email_subj, text_body, html_body)

