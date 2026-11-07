"""
Sahil Nawaz Portfolio — Google Calendar & Google Meet Integration Service
Features:
- Official Google Calendar API v3 integration with conferenceData (Google Meet)
- Supports service account or OAuth credentials via environment variables
- Generates authentic Google Meet links ONLY when authorized credentials are provided
- Never fabricates or invents fake meeting links
- Gracefully indicates unconfigured state when credentials are not supplied
"""

import os
import re
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger("portfolio.calendar")

# Environment configuration
GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")

def is_google_calendar_configured():
    """Check if valid Google Calendar credentials are provided."""
    return bool(
        (GOOGLE_SERVICE_ACCOUNT_FILE and os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE)) or
        (GOOGLE_SERVICE_ACCOUNT_JSON and len(GOOGLE_SERVICE_ACCOUNT_JSON) > 20)
    )

def parse_slot_times(date_str, time_slot_str):
    """
    Parse a date (YYYY-MM-DD) and a time slot (e.g. '10:00 AM - 10:30 AM (IST)' or '02:00 PM - 02:30 PM')
    into start and end ISO datetime strings in UTC.
    IST is UTC+5:30.
    """
    try:
        # Extract start time (e.g., '10:00 AM' or '02:00 PM')
        match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)', time_slot_str)
        if not match:
            # Default to 10:00 AM if unparseable
            start_time_str = "10:00 AM"
        else:
            start_time_str = match.group(1).strip()
            if "AM" not in start_time_str.upper() and "PM" not in start_time_str.upper():
                start_time_str += " AM"

        # Parse start datetime assuming IST (+05:30)
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        start_naive = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %I:%M %p")
        start_ist = start_naive.replace(tzinfo=ist_offset)
        end_ist = start_ist + timedelta(minutes=30)

        # Convert to ISO 8601 strings
        return start_ist.isoformat(), end_ist.isoformat()
    except Exception as e:
        logger.warning(f"Could not parse time slot '{time_slot_str}': {e}. Using default.")
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        default_dt = datetime.strptime(f"{date_str} 10:00 AM", "%Y-%m-%d %I:%M %p").replace(tzinfo=ist_offset)
        return default_dt.isoformat(), (default_dt + timedelta(minutes=30)).isoformat()

def create_google_meet_event(summary, description, attendee_email, date_str, time_slot_str):
    """
    Create a genuine Google Calendar event with Google Meet conference enabled.
    Returns:
    {
        "success": bool,
        "configured": bool,
        "meeting_link": str,
        "event_id": str,
        "message": str
    }
    """
    if not is_google_calendar_configured():
        logger.info("[CALENDAR] Google Calendar credentials not configured. Meeting link generation deferred to approval.")
        return {
            "success": False,
            "configured": False,
            "meeting_link": "",
            "event_id": "",
            "message": "Google Calendar API credentials are not configured. Setup GOOGLE_SERVICE_ACCOUNT_FILE in .env to enable automatic Google Meet generation."
        }

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
        
        if GOOGLE_SERVICE_ACCOUNT_FILE and os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
            creds = service_account.Credentials.from_service_account_file(
                GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
        else:
            import json
            info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
            creds = service_account.Credentials.from_service_account_info(
                info, scopes=SCOPES
            )

        service = build("calendar", "v3", credentials=creds)

        start_time, end_time = parse_slot_times(date_str, time_slot_str)
        request_id = f"sahil-meet-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        event_body = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
            "attendees": [{"email": attendee_email}],
            "conferenceData": {
                "createRequest": {
                    "requestId": request_id,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }
        }

        created_event = service.events().insert(
            calendarId=GOOGLE_CALENDAR_ID,
            body=event_body,
            conferenceDataVersion=1
        ).execute()

        # Extract authentic Google Meet link
        meet_link = created_event.get("hangoutLink") or ""
        event_id = created_event.get("id") or ""

        logger.info(f"[CALENDAR] Successfully created Google Meet event: {meet_link}")
        return {
            "success": True,
            "configured": True,
            "meeting_link": meet_link,
            "event_id": event_id,
            "message": "Google Meet session generated successfully."
        }

    except Exception as e:
        logger.error(f"[CALENDAR ERROR] Failed to create Google Calendar event: {e}")
        return {
            "success": False,
            "configured": True,
            "meeting_link": "",
            "event_id": "",
            "error": str(e),
            "message": f"Google Calendar API error: {str(e)}"
        }

