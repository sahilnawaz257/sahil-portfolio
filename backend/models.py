from database import get_db_connection

class Contact:
    @staticmethod
    def create(name, email, subject, message):
        """Save a new contact message into the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contacts (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        """, (name.strip(), email.strip(), subject.strip() if subject else "", message.strip()))
        conn.commit()
        contact_id = cursor.lastrowid
        conn.close()
        return contact_id

    @staticmethod
    def get_all():
        """Retrieve all submitted messages ordered by newest first."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(contact_id):
        """Retrieve a specific contact message by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def mark_as_read(contact_id):
        """Mark a contact message as read."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE contacts SET status = 'read' WHERE id = ?", (contact_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0

    @staticmethod
    def delete(contact_id):
        """Delete a contact message by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0


class Project:
    @staticmethod
    def get_all(category=None, featured_only=False):
        """Retrieve projects with optional category and featured filtering."""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM projects WHERE 1=1"
        params = []

        if category and category.lower() != "all":
            query += " AND category = ?"
            params.append(category.lower())

        if featured_only:
            query += " AND featured = 1"

        query += " ORDER BY featured DESC, id ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            p = dict(row)
            # Split comma-separated tech stack into an array for easy frontend rendering
            p["tech_list"] = [t.strip() for t in p["tech_stack"].split(",") if t.strip()]
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
        p["tech_list"] = [t.strip() for t in p["tech_stack"].split(",") if t.strip()]
        return p

    @staticmethod
    def get_by_slug(slug):
        """Retrieve a specific project by slug."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        p = dict(row)
        p["tech_list"] = [t.strip() for t in p["tech_stack"].split(",") if t.strip()]
        return p

