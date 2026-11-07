"""
Sahil Nawaz Portfolio — Database Models (Phase 2)
Provides SQLite CRUD operations for contact messages, projects, and admin authentication.
"""

from database import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash

class ContactMessage:
    """Manages visitor inquiries submitted through the contact form."""

    @staticmethod
    def create(full_name, email, subject, message):
        """Insert a validated contact message into SQLite."""
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

    @staticmethod
    def delete(msg_id):
        """Delete a contact message by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contact_messages WHERE id = ?", (msg_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted


class Project:
    """Manages portfolio project records in SQLite."""

    @staticmethod
    def get_all():
        """Retrieve all projects ordered by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            p = dict(row)
            # Parse technologies into list for clean JSON delivery
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

    @staticmethod
    def create(title, description, technologies, github_url="", live_demo_url=""):
        """Create a new project record."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (title, description, technologies, github_url, live_demo_url)
            VALUES (?, ?, ?, ?, ?)
        """, (
            title.strip(),
            description.strip(),
            technologies.strip(),
            github_url.strip() if github_url else "",
            live_demo_url.strip() if live_demo_url else ""
        ))
        conn.commit()
        project_id = cursor.lastrowid
        conn.close()
        return project_id

    @staticmethod
    def update(project_id, title, description, technologies, github_url="", live_demo_url=""):
        """Update an existing project record."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects
            SET title = ?, description = ?, technologies = ?, github_url = ?, live_demo_url = ?
            WHERE id = ?
        """, (
            title.strip(),
            description.strip(),
            technologies.strip(),
            github_url.strip() if github_url else "",
            live_demo_url.strip() if live_demo_url else "",
            project_id
        ))
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

    @staticmethod
    def delete(project_id):
        """Delete a project record."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted


class AdminUser:
    """Manages admin credentials and secure authentication."""

    @staticmethod
    def verify_password(username, password):
        """Verify username and password against SQLite hashed credentials."""
        if not username or not password:
            return False
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin_users WHERE username = ?", (username.strip(),))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            return True
        return False

    @staticmethod
    def create(username, password):
        """Create a new admin user with hashed password."""
        conn = get_db_connection()
        cursor = conn.cursor()
        pw_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO admin_users (username, password_hash)
            VALUES (?, ?)
        """, (username.strip(), pw_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
