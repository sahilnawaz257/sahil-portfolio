"""
Sahil Nawaz Portfolio — Database Models (Dual-Engine PostgreSQL / SQLite)
Provides object-level interfaces for all 6 portfolio tables:
- contact_messages
- meeting_bookings
- projects
- education
- experience
- skills

Zero Admin Functionality: Dedicated strictly to visitor form submissions and public portfolio retrieval.
"""

from database import (
    save_contact_message,
    check_duplicate_contact,
    save_meeting_booking,
    check_duplicate_booking,
    get_meeting_booking_by_id,
    get_portfolio_projects,
    get_project_by_id,
    get_education_records,
    get_experience_records,
    get_skills_inventory,
    execute_query
)

class ContactMessage:
    """Manages visitor inquiries submitted through the contact form."""

    @staticmethod
    def create(full_name, email, subject, message):
        """Insert a validated contact message using parameterized query."""
        return save_contact_message(
            full_name=full_name,
            email=email,
            subject=subject,
            message=message
        )

    @staticmethod
    def check_duplicate(email, message, window_seconds=60):
        """Check for recently submitted identical message."""
        return check_duplicate_contact(email, message, window_seconds=window_seconds)

    @staticmethod
    def get_by_id(msg_id):
        """Retrieve a single message by ID (internal only)."""
        sql = "SELECT * FROM contact_messages WHERE id = %s"
        return execute_query(sql, (msg_id,), fetch="one")


class MeetingBooking:
    """Manages Google Meet scheduling appointments."""

    @staticmethod
    def create(full_name, email, purpose, preferred_date=None, preferred_time=None, meeting_date=None, meeting_time=None, notes=""):
        """Insert a new meeting booking request."""
        p_date = preferred_date or meeting_date or ""
        p_time = preferred_time or meeting_time or ""
        return save_meeting_booking(
            full_name=full_name,
            email=email,
            purpose=purpose,
            preferred_date=p_date,
            preferred_time=p_time,
            notes=notes
        )

    @staticmethod
    def check_duplicate(email, preferred_date, preferred_time):
        """Check if an active booking exists for this email or slot."""
        return check_duplicate_booking(email, preferred_date, preferred_time)

    @staticmethod
    def get_by_id(booking_id):
        """Retrieve booking details by ID."""
        return get_meeting_booking_by_id(booking_id)


class Project:
    """Manages portfolio project records."""

    @staticmethod
    def get_all():
        """Retrieve all projects ordered by ID with parsed technology lists."""
        return get_portfolio_projects()

    @staticmethod
    def get_by_id(project_id):
        """Retrieve a specific project by ID."""
        return get_project_by_id(project_id)


class Education:
    """Manages verified academic degree records."""

    @staticmethod
    def get_all():
        """Retrieve all formal education records."""
        return get_education_records()


class Experience:
    """Manages professional venture and work track records."""

    @staticmethod
    def get_all():
        """Retrieve all professional experience records."""
        return get_experience_records()


class Skill:
    """Manages technical and product/business skill items."""

    @staticmethod
    def get_all():
        """Retrieve all skills."""
        inv = get_skills_inventory()
        return inv["skills"]

    @staticmethod
    def get_grouped():
        """Retrieve skills grouped by category."""
        inv = get_skills_inventory()
        return inv["categories"]
