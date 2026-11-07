"""
Sahil Nawaz Portfolio — Database Models (Dual-Engine PostgreSQL / SQLite)
Provides parameterized query operations for all 6 portfolio tables:
- contact_messages
- meeting_bookings
- projects
- education
- experience
- skills

Zero Admin Functionality: Only public read operations and visitor form submissions.
"""

from database import execute_query, insert_and_get_id

class ContactMessage:
    """Manages visitor inquiries submitted through the contact form."""

    @staticmethod
    def create(full_name, email, subject, message):
        """Insert a validated contact message using parameterized query."""
        sql = """
            INSERT INTO contact_messages (full_name, email, subject, message)
            VALUES (%s, %s, %s, %s)
        """
        return insert_and_get_id(sql, (
            full_name.strip(),
            email.strip(),
            subject.strip() if subject else "",
            message.strip()
        ), id_col="id")

    @staticmethod
    def get_by_id(msg_id):
        """Retrieve a single message by ID."""
        sql = "SELECT * FROM contact_messages WHERE id = %s"
        return execute_query(sql, (msg_id,), fetch="one")


class MeetingBooking:
    """Manages Google Meet scheduling appointments."""

    @staticmethod
    def create(full_name, email, purpose, preferred_date=None, preferred_time=None, meeting_date=None, meeting_time=None, notes=""):
        """Insert a new meeting booking request (supports both preferred_date and meeting_date)."""
        from database import is_postgres
        p_date = preferred_date or meeting_date or ""
        p_time = preferred_time or meeting_time or ""

        if is_postgres():
            sql = """
                INSERT INTO meeting_bookings (full_name, email, purpose, preferred_date, preferred_time, status, notes)
                VALUES (%s, %s, %s, %s, %s, 'Pending', %s)
            """
            return insert_and_get_id(sql, (
                full_name.strip(),
                email.strip(),
                purpose.strip(),
                str(p_date).strip(),
                str(p_time).strip(),
                notes.strip() if notes else ""
            ), id_col="id")
        else:
            sql = """
                INSERT INTO meeting_bookings (full_name, email, purpose, preferred_date, preferred_time, meeting_date, meeting_time, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending', %s)
            """
            return insert_and_get_id(sql, (
                full_name.strip(),
                email.strip(),
                purpose.strip(),
                str(p_date).strip(),
                str(p_time).strip(),
                str(p_date).strip(),
                str(p_time).strip(),
                notes.strip() if notes else ""
            ), id_col="id")

    @staticmethod
    def check_duplicate(email, preferred_date, preferred_time):
        """Check if an active booking exists for this email or slot."""
        sql = """
            SELECT * FROM meeting_bookings
            WHERE email = %s 
              AND (preferred_date = %s OR meeting_date = %s)
              AND (preferred_time = %s OR meeting_time = %s)
              AND status != 'Rejected'
        """
        return execute_query(sql, (
            email.strip(),
            str(preferred_date).strip(),
            str(preferred_date).strip(),
            str(preferred_time).strip(),
            str(preferred_time).strip()
        ), fetch="one")

    @staticmethod
    def get_by_id(booking_id):
        """Retrieve booking details by ID."""
        sql = "SELECT * FROM meeting_bookings WHERE id = %s"
        row = execute_query(sql, (booking_id,), fetch="one")
        if not row:
            return None
        # Normalize date/time/link fields across PostgreSQL & SQLite column names
        row["meeting_date"] = row.get("preferred_date") or row.get("meeting_date")
        row["meeting_time"] = row.get("preferred_time") or row.get("meeting_time")
        row["google_meet_link"] = row.get("meeting_link") or row.get("google_meet_link") or ""
        return row


class Project:
    """Manages portfolio project records."""

    @staticmethod
    def get_all():
        """Retrieve all projects ordered by ID with parsed technology lists."""
        sql = "SELECT * FROM projects ORDER BY id ASC"
        rows = execute_query(sql, fetch="all")
        results = []
        for p in rows:
            tech_str = p.get("technologies") or p.get("tech_stack") or ""
            p["technologies"] = tech_str
            p["tech_list"] = [t.strip() for t in tech_str.split(",") if t.strip()]
            if "live_demo_url" not in p or p["live_demo_url"] is None:
                p["live_demo_url"] = p.get("live_url") or ""
            results.append(p)
        return results

    @staticmethod
    def get_by_id(project_id):
        """Retrieve a specific project by ID."""
        sql = "SELECT * FROM projects WHERE id = %s"
        p = execute_query(sql, (project_id,), fetch="one")
        if not p:
            return None
        tech_str = p.get("technologies") or p.get("tech_stack") or ""
        p["technologies"] = tech_str
        p["tech_list"] = [t.strip() for t in tech_str.split(",") if t.strip()]
        if "live_demo_url" not in p or p["live_demo_url"] is None:
            p["live_demo_url"] = p.get("live_url") or ""
        return p


class Education:
    """Manages verified academic degree records."""

    @staticmethod
    def get_all():
        """Retrieve all formal education records."""
        sql = "SELECT * FROM education ORDER BY id ASC"
        return execute_query(sql, fetch="all")


class Experience:
    """Manages professional venture and work track records."""

    @staticmethod
    def get_all():
        """Retrieve all professional experience records."""
        sql = "SELECT * FROM experience ORDER BY id ASC"
        return execute_query(sql, fetch="all")


class Skill:
    """Manages technical and product/business skill items."""

    @staticmethod
    def get_all():
        """Retrieve all skills."""
        sql = "SELECT * FROM skills ORDER BY id ASC"
        return execute_query(sql, fetch="all")

    @staticmethod
    def get_grouped():
        """Retrieve skills grouped by category."""
        rows = Skill.get_all()
        grouped = {}
        for r in rows:
            cat = r["category"]
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(r["skill_name"])
        return grouped
