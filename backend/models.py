"""
Sahil Nawaz Portfolio — Database Models
Provides SQLite operations for contact message storage and dynamic projects retrieval.
"""

from database import get_db_connection

class ContactMessage:
    """Manages visitor inquiries submitted through the contact form."""

    @staticmethod
    def create(full_name, email, subject, message):
        """Insert a validated contact message into SQLite using parameterized query."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contact_messages (full_name, email, subject, message)
            VALUES (?, ?, ?, ?)
        """, (full_name.strip(), email.strip(), subject.strip() if subject else "", message.strip()))
        conn.commit()
        msg_id = cursor.lastrowid
        conn.close()
        return msg_id

    @staticmethod
    def get_all():
        """Retrieve all messages sorted by newest first."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contact_messages ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(msg_id):
        """Retrieve a single message by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contact_messages WHERE id = ?", (msg_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None


class Project:
    """Manages portfolio project records in SQLite."""

    @staticmethod
    def get_all():
        """Retrieve all projects ordered by ID with parsed technology lists."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            p = dict(row)
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        p = dict(row)
        tech_str = p.get("technologies") or p.get("tech_stack") or ""
        p["technologies"] = tech_str
        p["tech_list"] = [t.strip() for t in tech_str.split(",") if t.strip()]
        if "live_demo_url" not in p or p["live_demo_url"] is None:
            p["live_demo_url"] = p.get("live_url") or ""
        return p


class MeetingBooking:
    """Manages Google Meet scheduling appointments in SQLite."""

    @staticmethod
    def create(full_name, email, purpose, meeting_date, meeting_time, notes=""):
        """Insert a new meeting booking request into SQLite."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO meeting_bookings (full_name, email, purpose, meeting_date, meeting_time, status, notes)
            VALUES (?, ?, ?, ?, ?, 'Pending', ?)
        """, (full_name.strip(), email.strip(), purpose.strip(), meeting_date.strip(), meeting_time.strip(), notes.strip() if notes else ""))
        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()
        return booking_id

    @staticmethod
    def check_duplicate(email, meeting_date, meeting_time):
        """Check if an active booking exists for this email or slot."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM meeting_bookings
            WHERE email = ? AND meeting_date = ? AND meeting_time = ? AND status != 'Rejected'
        """, (email.strip(), meeting_date.strip(), meeting_time.strip()))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_id(booking_id):
        """Retrieve booking details by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM meeting_bookings WHERE id = ?", (booking_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

