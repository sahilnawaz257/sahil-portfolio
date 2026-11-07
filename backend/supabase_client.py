"""
Sahil Nawaz Portfolio — Supabase Python SDK Integration Module
Features:
- Official Supabase Python SDK (supabase >= 2.3.0)
- Configured using:
    SUPABASE_URL
    SUPABASE_PUBLISHABLE_KEY
    SUPABASE_SECRET_KEY
- Secure Server-Side Operations: Secret key is never exposed to frontend or API responses
- Full CRUD operations via PostgREST Data API for all 6 tables:
    1. contact_messages
    2. meeting_bookings
    3. projects
    4. education
    5. experience
    6. skills
- Privacy Segregation: Visitor inquiries & bookings are private, portfolio data is public
- Dual-Engine Compatibility: Graceful SQLite fallback when Supabase credentials are unconfigured
"""

import os
import sys
import logging
from datetime import datetime, timezone

# Try loading environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("portfolio.supabase")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [SUPABASE] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ------------------------------------------------------------------------------
# 01. Credentials Configuration
# ------------------------------------------------------------------------------
SUPABASE_URL = (os.environ.get("SUPABASE_URL") or "").strip()
SUPABASE_PUBLISHABLE_KEY = (
    os.environ.get("SUPABASE_PUBLISHABLE_KEY") or
    os.environ.get("SUPABASE_ANON_KEY") or
    ""
).strip()
SUPABASE_SECRET_KEY = (
    os.environ.get("SUPABASE_SECRET_KEY") or
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or
    os.environ.get("SUPABASE_KEY") or
    ""
).strip()

_SUPABASE_CLIENT = None
_SUPABASE_INIT_ATTEMPTED = False

def is_placeholder(val):
    """Check if value is a placeholder string."""
    if not val:
        return True
    lower = val.lower()
    return any(p in lower for p in ["your_", "your-", "example.com", "placeholder", "[your"])

def is_supabase_configured():
    """
    Return True only if valid (non-placeholder) SUPABASE_URL and SECRET/PUBLISHABLE keys are defined.
    """
    if not SUPABASE_URL or not (SUPABASE_SECRET_KEY or SUPABASE_PUBLISHABLE_KEY):
        return False
    if is_placeholder(SUPABASE_URL):
        return False
    active_key = SUPABASE_SECRET_KEY or SUPABASE_PUBLISHABLE_KEY
    if is_placeholder(active_key):
        return False
    return True

def get_supabase_client():
    """
    Return initialized Supabase client singleton using the official Python SDK.
    Uses the secret key for authorized server-side execution.
    Never exposes keys to the frontend.
    """
    global _SUPABASE_CLIENT, _SUPABASE_INIT_ATTEMPTED
    if _SUPABASE_CLIENT is not None:
        return _SUPABASE_CLIENT

    if not is_supabase_configured():
        return None

    if _SUPABASE_INIT_ATTEMPTED and _SUPABASE_CLIENT is None:
        return None

    _SUPABASE_INIT_ATTEMPTED = True

    try:
        from supabase import create_client, Client

        # Prioritize SECRET_KEY for server-side operations (bypasses RLS for secure backend processing)
        api_key = SUPABASE_SECRET_KEY if SUPABASE_SECRET_KEY and not is_placeholder(SUPABASE_SECRET_KEY) else SUPABASE_PUBLISHABLE_KEY

        # Safe logging without exposing keys
        masked_url = SUPABASE_URL.split("//")[-1]
        logger.info(f"Initializing official Supabase Python SDK client for {masked_url}...")

        _SUPABASE_CLIENT = create_client(SUPABASE_URL, api_key)
        logger.info("Supabase Python SDK client successfully initialized.")
        return _SUPABASE_CLIENT

    except Exception as e:
        _SUPABASE_CLIENT = None
        logger.warning(f"Failed to initialize Supabase Python SDK: {str(e).splitlines()[0]}")
        return None

def check_supabase_connection():
    """
    Perform a safe health check against the Supabase PostgREST Data API.
    Returns: {"connected": bool, "engine": "supabase" | "sqlite_fallback", "message": str}
    """
    client = get_supabase_client()
    if not client:
        return {
            "connected": False,
            "engine": "sqlite_fallback",
            "message": "Supabase credentials are not configured or are placeholder values. Operating in local SQLite fallback mode."
        }

    try:
        # Lightweight read query to verify API credentials
        res = client.table("projects").select("id").limit(1).execute()
        return {
            "connected": True,
            "engine": "supabase",
            "status": "healthy",
            "message": f"Successfully connected to Supabase Data API ({SUPABASE_URL.split('//')[-1]})."
        }
    except Exception as e:
        err_msg = str(e).splitlines()[0] if str(e) else "Connection failed"
        logger.warning(f"Supabase Data API health check failed: {err_msg}")
        return {
            "connected": False,
            "engine": "sqlite_fallback",
            "error": err_msg,
            "message": f"Could not reach Supabase Data API ({err_msg}). Falling back to local SQLite engine."
        }

# ------------------------------------------------------------------------------
# 02. Reusable Supabase Data API Functions (6 Tables)
# ------------------------------------------------------------------------------

# --- 1. Contact Messages (Private: Visitor submission only) ---
def supabase_save_contact_message(full_name, email, subject, message):
    """Save visitor message to Supabase contact_messages table."""
    client = get_supabase_client()
    if not client:
        raise RuntimeError("Supabase client is not available")

    payload = {
        "full_name": full_name.strip(),
        "email": email.strip(),
        "subject": subject.strip() if subject else "",
        "message": message.strip()
    }
    res = client.table("contact_messages").insert(payload).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]["id"]
    return None

def supabase_check_duplicate_contact(email, message, window_seconds=60):
    """Check if an identical message was recently submitted to Supabase."""
    client = get_supabase_client()
    if not client:
        return None

    try:
        res = (
            client.table("contact_messages")
            .select("id, created_at")
            .eq("email", email.strip())
            .eq("message", message.strip())
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if res.data and len(res.data) > 0:
            row = res.data[0]
            raw_ts = row.get("created_at")
            if raw_ts:
                clean_ts = raw_ts.replace("Z", "+00:00")
                created_dt = datetime.fromisoformat(clean_ts)
                now_dt = datetime.now(timezone.utc)
                if (now_dt - created_dt).total_seconds() < window_seconds:
                    return row
            return None
        return None
    except Exception as e:
        logger.warning(f"Error checking duplicate contact in Supabase: {e}")
        return None

def supabase_get_contact_message_by_id(msg_id):
    """Retrieve message by ID for internal verification (Not public)."""
    client = get_supabase_client()
    if not client:
        return None
    res = client.table("contact_messages").select("*").eq("id", str(msg_id)).limit(1).execute()
    return res.data[0] if (res.data and len(res.data) > 0) else None


# --- 2. Meeting Bookings (Private: Visitor scheduling only) ---
def supabase_save_meeting_booking(full_name, email, purpose, preferred_date, preferred_time, notes=""):
    """Save booking request to Supabase meeting_bookings table."""
    client = get_supabase_client()
    if not client:
        raise RuntimeError("Supabase client is not available")

    payload = {
        "full_name": full_name.strip(),
        "email": email.strip(),
        "purpose": purpose.strip(),
        "preferred_date": str(preferred_date).strip(),
        "preferred_time": str(preferred_time).strip(),
        "status": "Pending",
        "notes": notes.strip() if notes else "",
        "meeting_link": ""
    }
    res = client.table("meeting_bookings").insert(payload).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]["id"]
    return None

def supabase_check_duplicate_booking(email, preferred_date, preferred_time):
    """Check for duplicate active booking in Supabase."""
    client = get_supabase_client()
    if not client:
        return None
    try:
        res = (
            client.table("meeting_bookings")
            .select("*")
            .eq("email", email.strip())
            .eq("preferred_date", str(preferred_date).strip())
            .eq("preferred_time", str(preferred_time).strip())
            .neq("status", "Rejected")
            .limit(1)
            .execute()
        )
        return res.data[0] if (res.data and len(res.data) > 0) else None
    except Exception as e:
        logger.warning(f"Error checking duplicate booking in Supabase: {e}")
        return None

def supabase_get_booked_slots(date_str):
    """Retrieve all booked slots for a specific date in Supabase."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        res = (
            client.table("meeting_bookings")
            .select("preferred_time")
            .eq("preferred_date", str(date_str).strip())
            .neq("status", "Rejected")
            .execute()
        )
        return [r["preferred_time"] for r in (res.data or []) if r.get("preferred_time")]
    except Exception as e:
        logger.warning(f"Error querying booked slots in Supabase: {e}")
        return []

def supabase_update_booking_status(booking_id, status, meeting_link=""):
    """Update booking status and meeting link in Supabase."""
    client = get_supabase_client()
    if not client:
        raise RuntimeError("Supabase client is not available")

    update_payload = {"status": status}
    if meeting_link:
        update_payload["meeting_link"] = meeting_link.strip()

    res = client.table("meeting_bookings").update(update_payload).eq("id", str(booking_id)).execute()
    if res.data and len(res.data) > 0:
        row = res.data[0]
        row["meeting_date"] = row.get("preferred_date")
        row["meeting_time"] = row.get("preferred_time")
        row["google_meet_link"] = row.get("meeting_link") or ""
        return row
    return supabase_get_meeting_booking_by_id(booking_id)

def supabase_get_meeting_booking_by_id(booking_id):
    """Retrieve booking by ID from Supabase."""
    client = get_supabase_client()
    if not client:
        return None
    try:
        res = client.table("meeting_bookings").select("*").eq("id", str(booking_id)).limit(1).execute()
        if res.data and len(res.data) > 0:
            row = res.data[0]
            row["meeting_date"] = row.get("preferred_date")
            row["meeting_time"] = row.get("preferred_time")
            row["google_meet_link"] = row.get("meeting_link") or ""
            return row
        return None
    except Exception as e:
        logger.warning(f"Error fetching booking from Supabase: {e}")
        return None

def supabase_get_pending_bookings():
    """Retrieve all pending booking requests from Supabase."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        res = (
            client.table("meeting_bookings")
            .select("*")
            .eq("status", "Pending")
            .order("created_at", desc=True)
            .execute()
        )
        rows = res.data or []
        for r in rows:
            r["meeting_date"] = r.get("preferred_date")
            r["meeting_time"] = r.get("preferred_time")
            r["google_meet_link"] = r.get("meeting_link") or ""
        return rows
    except Exception as e:
        logger.warning(f"Error retrieving pending bookings from Supabase: {e}")
        return []


# --- 3. Projects (Public: Read-only) ---
def supabase_get_projects():
    """Retrieve all portfolio projects from Supabase Data API."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        res = client.table("projects").select("*").order("created_at", desc=False).execute()
        projects = res.data or []
        for p in projects:
            tech_str = p.get("technologies") or p.get("tech_stack") or ""
            p["technologies"] = tech_str
            p["tech_list"] = [t.strip() for t in tech_str.split(",") if t.strip()]
            if "live_demo_url" not in p or p["live_demo_url"] is None:
                p["live_demo_url"] = p.get("live_url") or ""
        return projects
    except Exception as e:
        logger.warning(f"Error fetching projects from Supabase: {e}")
        return []

def supabase_get_project_by_id(project_id):
    """Retrieve details for a single project from Supabase."""
    client = get_supabase_client()
    if not client:
        return None
    try:
        res = client.table("projects").select("*").eq("id", str(project_id)).limit(1).execute()
        if res.data and len(res.data) > 0:
            p = res.data[0]
            tech_str = p.get("technologies") or p.get("tech_stack") or ""
            p["technologies"] = tech_str
            p["tech_list"] = [t.strip() for t in tech_str.split(",") if t.strip()]
            if "live_demo_url" not in p or p["live_demo_url"] is None:
                p["live_demo_url"] = p.get("live_url") or ""
            return p
        return None
    except Exception as e:
        logger.warning(f"Error fetching project by id from Supabase: {e}")
        return None


# --- 4. Education (Public: Read-only) ---
def supabase_get_education():
    """Retrieve formal education records from Supabase."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        res = client.table("education").select("*").order("start_date", desc=True).execute()
        return res.data or []
    except Exception as e:
        logger.warning(f"Error fetching education from Supabase: {e}")
        return []


# --- 5. Experience (Public: Read-only) ---
def supabase_get_experience():
    """Retrieve professional venture records from Supabase."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        res = client.table("experience").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        logger.warning(f"Error fetching experience from Supabase: {e}")
        return []


# --- 6. Skills (Public: Read-only) ---
def supabase_get_skills():
    """Retrieve full skill inventory and grouped categories from Supabase."""
    client = get_supabase_client()
    if not client:
        return {"skills": [], "categories": {}}
    try:
        res = client.table("skills").select("*").order("category").execute()
        skills = res.data or []
        categories = {}
        for s in skills:
            cat = s["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(s["skill_name"])
        return {
            "skills": skills,
            "categories": categories
        }
    except Exception as e:
        logger.warning(f"Error fetching skills from Supabase: {e}")
        return {"skills": [], "categories": {}}


# ------------------------------------------------------------------------------
# 03. Automatic Data Seeder for Supabase
# ------------------------------------------------------------------------------
def seed_supabase_if_empty():
    """
    If connected to Supabase and tables are empty, seeds default authentic portfolio data.
    Ensures zero duplicate inserts.
    """
    client = get_supabase_client()
    if not client:
        return

    try:
        # Check projects
        p_res = client.table("projects").select("id").limit(1).execute()
        if not p_res.data:
            logger.info("Seeding initial authentic projects to Supabase...")
            client.table("projects").insert([
                {
                    "title": "Crowd Density Counting System",
                    "description": "A technology-based system designed to monitor and count crowd density using computer vision and deep learning.",
                    "technologies": "Python, AI / ML, YOLOv8",
                    "github_url": "https://github.com/sahilnawaz257",
                    "live_demo_url": ""
                },
                {
                    "title": "Library Management Software",
                    "description": "A software solution to manage library books, student records and transactions with automated persistence.",
                    "technologies": "Python, SQL, SQLite",
                    "github_url": "https://github.com/sahilnawaz257",
                    "live_demo_url": ""
                },
                {
                    "title": "Brand Guideline Audit Tool",
                    "description": "A tool designed to check brand consistency, typography compliance, and visual palette auditing.",
                    "technologies": "HTML, CSS, JavaScript",
                    "github_url": "https://github.com/sahilnawaz257",
                    "live_demo_url": ""
                }
            ]).execute()

        # Check education
        e_res = client.table("education").select("id").limit(1).execute()
        if not e_res.data:
            logger.info("Seeding education records to Supabase...")
            client.table("education").insert([
                {
                    "institution": "JB Group of Institutions of Technology",
                    "degree": "Bachelor of Technology (B.Tech)",
                    "field": "Computer Science and Engineering (CSE)",
                    "location": "Dehradun, Uttarakhand, India",
                    "start_date": "2025",
                    "end_date": "2029",
                    "status": "Current (2nd Year)",
                    "logo_url": "images/jbit-dehradun-logo.png"
                },
                {
                    "institution": "The Open University",
                    "degree": "Data Analyst Online",
                    "field": "Computer Science (AI & LangChain RAG)",
                    "location": "United Kingdom (Online)",
                    "start_date": "June 2026",
                    "end_date": "July 2029",
                    "status": "Enrolled / Upcoming",
                    "logo_url": "images/the-open-university-logo.png"
                }
            ]).execute()

        # Check experience
        ex_res = client.table("experience").select("id").limit(1).execute()
        if not ex_res.data:
            logger.info("Seeding experience records to Supabase...")
            client.table("experience").insert([
                {
                    "company_name": "Gymsewa",
                    "role": "Founder",
                    "duration": "2024 – Present",
                    "description": "Founder of Gymsewa, working on building and developing a business-focused platform. Responsible for product planning, business development, platform strategy, innovation and overall project direction.",
                    "powered_by": "Bytewave Innovation"
                }
            ]).execute()

    except Exception as e:
        logger.warning(f"Supabase data seeding notice: {e}")
