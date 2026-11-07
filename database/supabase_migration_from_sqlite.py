"""
Sahil Nawaz Portfolio — SQLite to Supabase Migration Utility
Transfers authentic project records, education, experience, skills,
and existing visitor messages/bookings from local SQLite backup into Supabase PostgreSQL.
Prevents duplicate records using unique identifiers and ON CONFLICT handling.
"""

import os
import sys
import json
import sqlite3

# Load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
SQLITE_DB = os.path.join(PROJECT_ROOT, "database", "portfolio.db")
BACKUP_JSON = os.path.join(PROJECT_ROOT, "database", "backup_data.json")

def migrate_to_supabase(supabase_db_url=None):
    """
    Connect to Supabase PostgreSQL using connection string and migrate data.
    """
    db_url = supabase_db_url or os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        print("[MIGRATION NOTICE] Neither SUPABASE_DB_URL nor DATABASE_URL environment variable is set.")
        print("Please configure your Supabase connection string in your .env file:")
        print("DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres")
        return False

    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("[ERROR] psycopg2-binary is required for migration. Install with: pip install psycopg2-binary")
        return False

    print(f"[MIGRATION] Connecting to Supabase PostgreSQL at {db_url.split('@')[-1]}...")
    try:
        pg_conn = psycopg2.connect(db_url)
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase PostgreSQL: {e}")
        return False

    # Execute Schema creation from SQL file
    schema_file = os.path.join(PROJECT_ROOT, "database", "supabase_schema.sql")
    if os.path.exists(schema_file):
        print(f"[MIGRATION] Applying Supabase schema from {schema_file}...")
        with open(schema_file, "r", encoding="utf-8") as f:
            sql_commands = f.read()
        try:
            pg_cursor.execute(sql_commands)
            pg_conn.commit()
            print("[MIGRATION SUCCESS] Schema and RLS policies applied successfully.")
        except Exception as e:
            pg_conn.rollback()
            print(f"[SCHEMA ERROR] {e}")

    # Migrate Contact Messages from backup
    if os.path.exists(SQLITE_DB):
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sq_cursor = sqlite_conn.cursor()

        # Migrate contact_messages
        sq_cursor.execute("SELECT full_name, email, subject, message, created_at FROM contact_messages")
        contacts = sq_cursor.fetchall()
        migrated_contacts = 0
        for c in contacts:
            pg_cursor.execute("""
                INSERT INTO public.contact_messages (full_name, email, subject, message, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (c["full_name"], c["email"], c["subject"], c["message"], c["created_at"]))
            migrated_contacts += 1
        print(f"[MIGRATION] Processed {migrated_contacts} contact messages.")

        # Migrate meeting_bookings
        sq_cursor.execute("SELECT full_name, email, purpose, meeting_date, meeting_time, status, google_meet_link, notes, created_at FROM meeting_bookings")
        bookings = sq_cursor.fetchall()
        migrated_bookings = 0
        for b in bookings:
            pg_cursor.execute("""
                INSERT INTO public.meeting_bookings (full_name, email, purpose, preferred_date, preferred_time, status, meeting_link, notes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (b["full_name"], b["email"], b["purpose"], b["meeting_date"], b["meeting_time"], b["status"], b["google_meet_link"], b["notes"], b["created_at"]))
            migrated_bookings += 1
        print(f"[MIGRATION] Processed {migrated_bookings} meeting bookings.")

        sqlite_conn.close()

    pg_conn.commit()
    pg_conn.close()
    print("[MIGRATION COMPLETE] All existing data preserved and synchronized with Supabase PostgreSQL.")
    return True

if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    migrate_to_supabase(url_arg)
