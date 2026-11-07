"""
Sahil Nawaz Portfolio — Database Connection & Query Module (Supabase PostgreSQL + SQLite Fallback)
Features:
- Dedicated PostgreSQL connection pooling via psycopg2.pool.ThreadedConnectionPool
- Supports SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD
- Secure SSL connection settings (sslmode=require)
- Automated connection error handling & safe error sanitization (no credential leakage)
- 100% Parameterized SQL queries for SQL injection immunity
- Reusable functions for saving messages/bookings and reading public portfolio data
- Zero Admin Dashboard / Zero Admin Tables
"""

import os
import re
import sys
import logging
from contextlib import contextmanager

# Try loading environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Setup logger for database operations
logger = logging.getLogger("portfolio.database")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [DB] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
SQLITE_DB_PATH = os.path.join(DATABASE_DIR, "portfolio.db")

# ------------------------------------------------------------------------------
# 01. Supabase PostgreSQL Configuration & Credentials
# ------------------------------------------------------------------------------
SUPABASE_DB_HOST = os.environ.get("SUPABASE_DB_HOST")
SUPABASE_DB_PORT = os.environ.get("SUPABASE_DB_PORT", "5432")
SUPABASE_DB_NAME = os.environ.get("SUPABASE_DB_NAME", "postgres")
SUPABASE_DB_USER = os.environ.get("SUPABASE_DB_USER", "postgres")
SUPABASE_DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD")
PGSSLMODE = os.environ.get("PGSSLMODE", "require")

# Direct / Pooled URL fallback (if provided)
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL")

# Build connection string if individual parameters are supplied
if not DATABASE_URL and SUPABASE_DB_HOST and SUPABASE_DB_PASSWORD:
    DATABASE_URL = f"postgresql://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}?sslmode={PGSSLMODE}"

# Threaded connection pool instance for PostgreSQL
_PG_POOL = None
_PG_INITIALIZATION_ATTEMPTED = False
_IS_PG_ACTIVE = False

def is_postgres_configured():
    """Check if PostgreSQL credentials or connection URL are defined."""
    return bool(DATABASE_URL and DATABASE_URL.startswith(("postgres://", "postgresql://")))

def is_postgres():
    """Return True if PostgreSQL pool is active and operational."""
    global _IS_PG_ACTIVE
    return _IS_PG_ACTIVE

def get_connection_pool():
    """
    Initialize and return the ThreadedConnectionPool for Supabase PostgreSQL.
    Implements safe error handling and logging.
    """
    global _PG_POOL, _PG_INITIALIZATION_ATTEMPTED, _IS_PG_ACTIVE
    if _PG_POOL is not None:
        return _PG_POOL

    if not is_postgres_configured():
        return None

    if _PG_INITIALIZATION_ATTEMPTED and _PG_POOL is None:
        return None

    _PG_INITIALIZATION_ATTEMPTED = True

    try:
        import psycopg2
        from psycopg2 import pool
        from psycopg2.extras import RealDictCursor

        # Parse host for logging without exposing credentials
        host_match = re.search(r'@([^:/]+)', DATABASE_URL)
        safe_host = host_match.group(1) if host_match else "remote host"
        logger.info(f"Initializing connection pool to Supabase PostgreSQL at {safe_host} (SSL: {PGSSLMODE})...")

        _PG_POOL = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL,
            sslmode=PGSSLMODE,
            connect_timeout=5,
            cursor_factory=RealDictCursor
        )
        _IS_PG_ACTIVE = True
        logger.info("Supabase PostgreSQL connection pool initialized successfully.")
        return _PG_POOL

    except Exception as e:
        _IS_PG_ACTIVE = False
        _PG_POOL = None
        # Safe logging without leaking connection password
        err_msg = str(e).splitlines()[0] if str(e) else "Unknown error"
        logger.warning(f"Could not connect to Supabase PostgreSQL ({err_msg}). Falling back to local SQLite engine.")
        return None

def get_db_connection():
    """
    Return an active database connection.
    Borrows a connection from the Supabase pool if operational,
    or creates an SQLite connection with Row factory.
    """
    pg_pool = get_connection_pool()
    if pg_pool:
        try:
            conn = pg_pool.getconn()
            if conn:
                return conn
        except Exception as e:
            logger.warning(f"Failed to borrow connection from PostgreSQL pool: {e}. Falling back to SQLite.")

    import sqlite3
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def release_db_connection(conn):
    """Safely return a borrowed connection back to the pool or close SQLite connection."""
    global _PG_POOL
    if conn is None:
        return

    if is_postgres() and _PG_POOL is not None:
        try:
            _PG_POOL.putconn(conn)
            return
        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}")

    try:
        conn.close()
    except Exception:
        pass

def adapt_query(query):
    """
    Translate parameterized query placeholders:
    Uses %s for PostgreSQL and ? for SQLite.
    """
    if is_postgres():
        return query
    # Convert %s placeholder to ? for SQLite
    return re.sub(r'%s', '?', query)

@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager that acquires a connection, yields a dictionary cursor,
    commits if requested, handles rollbacks on error, and safely closes/returns resources.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        release_db_connection(conn)

def execute_query(query, params=(), fetch="none", commit=False):
    """
    Execute a parameterized SQL query with automatic placeholder adaptation.
    fetch: 'none', 'one', or 'all'
    """
    with get_db_cursor(commit=commit) as cursor:
        sql = adapt_query(query)
        cursor.execute(sql, params)
        if fetch == "one":
            row = cursor.fetchone()
            return dict(row) if row else None
        elif fetch == "all":
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        return None

def insert_and_get_id(query, params=(), id_col="id"):
    """
    Execute an INSERT statement and return the new row ID (UUID string or integer).
    """
    with get_db_cursor(commit=True) as cursor:
        if is_postgres():
            # In PostgreSQL, ensure RETURNING clause is present
            if not re.search(r'\breturning\b', query, re.I):
                sql = f"{query.rstrip(';')} RETURNING {id_col}"
            else:
                sql = query
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return row[id_col] if isinstance(row, dict) else row[0]
        else:
            sql = adapt_query(query)
            cursor.execute(sql, params)
            return cursor.lastrowid

# ------------------------------------------------------------------------------
# 02. Reusable Portfolio Database Functions (Public & Private Segregation)
# ------------------------------------------------------------------------------

def save_contact_message(full_name, email, subject, message):
    """
    Persist visitor contact form submission using parameterized query.
    Private: Stored securely, never readable by public API visitors.
    """
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

def check_duplicate_contact(email, message, window_seconds=60):
    """
    Check if an identical message was submitted by this email address recently.
    Prevents accidental duplicate form submissions and spam attacks.
    """
    clean_email = email.strip()
    clean_msg = message.strip()
    if is_postgres():
        sql = """
            SELECT id, created_at FROM contact_messages
            WHERE email = %s AND message = %s
              AND created_at > (now() - INTERVAL '60 seconds')
            LIMIT 1
        """
        return execute_query(sql, (clean_email, clean_msg), fetch="one")
    else:
        sql = """
            SELECT id, created_at FROM contact_messages
            WHERE email = %s AND message = %s
            ORDER BY id DESC LIMIT 1
        """
        row = execute_query(sql, (clean_email, clean_msg), fetch="one")
        if not row:
            return None
        raw_created = row.get("created_at")
        if raw_created:
            try:
                from datetime import datetime, timezone
                if isinstance(raw_created, str):
                    clean_ts = raw_created.replace("T", " ").split(".")[0]
                    created_dt = datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    now_dt = datetime.now(timezone.utc)
                    if (now_dt - created_dt).total_seconds() < window_seconds:
                        return row
            except Exception:
                return row
        return None

def save_meeting_booking(full_name, email, purpose, preferred_date, preferred_time, notes=""):
    """
    Persist visitor Google Meet scheduling request using parameterized query.
    Private: Inaccessible to unauthorized public scrapers.
    """
    p_date = str(preferred_date).strip()
    p_time = str(preferred_time).strip()

    if is_postgres():
        sql = """
            INSERT INTO meeting_bookings (full_name, email, purpose, preferred_date, preferred_time, status, notes)
            VALUES (%s, %s, %s, %s, %s, 'Pending', %s)
        """
        return insert_and_get_id(sql, (
            full_name.strip(),
            email.strip(),
            purpose.strip(),
            p_date,
            p_time,
            notes.strip() if notes else ""
        ), id_col="id")
    else:
        # SQLite dual-column compatibility for preferred_date and meeting_date
        sql = """
            INSERT INTO meeting_bookings (full_name, email, purpose, preferred_date, preferred_time, meeting_date, meeting_time, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending', %s)
        """
        return insert_and_get_id(sql, (
            full_name.strip(),
            email.strip(),
            purpose.strip(),
            p_date,
            p_time,
            p_date,
            p_time,
            notes.strip() if notes else ""
        ), id_col="id")

def check_duplicate_booking(email, preferred_date, preferred_time):
    """Check if an active booking already exists for this email or time slot."""
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

def get_meeting_booking_by_id(booking_id):
    """Retrieve booking details by ID (used for status checking)."""
    sql = "SELECT * FROM meeting_bookings WHERE id = %s"
    row = execute_query(sql, (booking_id,), fetch="one")
    if not row:
        return None
    row["meeting_date"] = row.get("preferred_date") or row.get("meeting_date")
    row["meeting_time"] = row.get("preferred_time") or row.get("meeting_time")
    row["google_meet_link"] = row.get("meeting_link") or row.get("google_meet_link") or ""
    return row

def get_booked_slots_for_date(date_str):
    """
    Retrieve all booked/pending time slots for a specified date.
    Ensures that only genuinely available time slots are presented to visitors.
    """
    d = str(date_str).strip()
    if is_postgres():
        sql = """
            SELECT preferred_time AS time_slot FROM meeting_bookings
            WHERE preferred_date = %s AND status != 'Rejected'
        """
        rows = execute_query(sql, (d,), fetch="all") or []
    else:
        sql = """
            SELECT COALESCE(preferred_time, meeting_time) AS time_slot FROM meeting_bookings
            WHERE (preferred_date = %s OR meeting_date = %s) AND status != 'Rejected'
        """
        rows = execute_query(sql, (d, d), fetch="all") or []
    return [r["time_slot"] for r in rows if r.get("time_slot")]

def update_booking_status(booking_id, status, meeting_link=""):
    """
    Update booking status (Pending -> Approved / Rejected) and set meeting link.
    Used exclusively by authorized owner approval workflow (HMAC token or backend CLI).
    """
    valid_statuses = ("Pending", "Approved", "Rejected")
    if status not in valid_statuses:
        raise ValueError(f"Invalid booking status '{status}'. Must be one of: {valid_statuses}")

    sql = """
        UPDATE meeting_bookings
        SET status = %s, meeting_link = COALESCE(NULLIF(%s, ''), meeting_link)
        WHERE id = %s
    """
    execute_query(sql, (status, meeting_link.strip(), booking_id), commit=True)
    return get_meeting_booking_by_id(booking_id)

def get_pending_bookings():
    """Retrieve all pending booking requests for owner review."""
    sql = "SELECT * FROM meeting_bookings WHERE status = 'Pending' ORDER BY created_at DESC" if is_postgres() else "SELECT * FROM meeting_bookings WHERE status = 'Pending' ORDER BY id DESC"
    rows = execute_query(sql, fetch="all") or []
    for r in rows:
        r["meeting_date"] = r.get("preferred_date") or r.get("meeting_date")
        r["meeting_time"] = r.get("preferred_time") or r.get("meeting_time")
        r["google_meet_link"] = r.get("meeting_link") or r.get("google_meet_link") or ""
    return rows

def get_portfolio_projects():
    """Retrieve all public portfolio projects with parsed technology stacks."""
    sql = "SELECT * FROM projects ORDER BY created_at ASC" if is_postgres() else "SELECT * FROM projects ORDER BY id ASC"
    rows = execute_query(sql, fetch="all") or []
    results = []
    for p in rows:
        tech_str = p.get("technologies") or p.get("tech_stack") or ""
        p["technologies"] = tech_str
        p["tech_list"] = [t.strip() for t in tech_str.split(",") if t.strip()]
        if "live_demo_url" not in p or p["live_demo_url"] is None:
            p["live_demo_url"] = p.get("live_url") or ""
        results.append(p)
    return results

def get_project_by_id(project_id):
    """Retrieve details for a single project by ID."""
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

def get_education_records():
    """Retrieve formal education records for public display."""
    sql = "SELECT * FROM education ORDER BY start_date DESC" if is_postgres() else "SELECT * FROM education ORDER BY id ASC"
    return execute_query(sql, fetch="all") or []

def get_experience_records():
    """Retrieve professional experience and venture leadership records for public display."""
    sql = "SELECT * FROM experience ORDER BY created_at DESC" if is_postgres() else "SELECT * FROM experience ORDER BY id ASC"
    return execute_query(sql, fetch="all") or []

def get_skills_inventory():
    """Retrieve full skill inventory and grouped category dictionary."""
    sql = "SELECT * FROM skills ORDER BY category ASC, skill_name ASC"
    skills = execute_query(sql, fetch="all") or []
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

# ------------------------------------------------------------------------------
# 03. Database Initialization & Schema Seeding
# ------------------------------------------------------------------------------

def init_db():
    """
    Initialize database schema (PostgreSQL or SQLite), drop legacy admin tables,
    and seed authentic portfolio data if empty.
    """
    # Trigger pool setup attempt
    get_connection_pool()

    with get_db_cursor(commit=True) as cursor:
        if is_postgres():
            # Apply PostgreSQL schema with UUID keys
            cursor.execute("""
                CREATE EXTENSION IF NOT EXISTS "pgcrypto";
                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

                CREATE TABLE IF NOT EXISTS public.contact_messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    subject TEXT DEFAULT '',
                    message TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS public.meeting_bookings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    preferred_date DATE NOT NULL,
                    preferred_time TEXT NOT NULL,
                    status TEXT DEFAULT 'Pending' NOT NULL,
                    meeting_link TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS public.projects (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    technologies TEXT NOT NULL,
                    github_url TEXT DEFAULT '',
                    live_demo_url TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS public.education (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    institution TEXT NOT NULL UNIQUE,
                    degree TEXT NOT NULL,
                    field TEXT NOT NULL,
                    location TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    logo_url TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS public.experience (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    company_name TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    description TEXT NOT NULL,
                    powered_by TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS public.skills (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    skill_name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
                );
            """)

            # Remove legacy admin tables
            cursor.execute("DROP TABLE IF EXISTS public.admin_users CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS public.contacts CASCADE;")

            # Seed Projects if empty
            cursor.execute("SELECT COUNT(*) as count FROM public.projects")
            p_count = cursor.fetchone()["count"]
            if p_count == 0:
                cursor.execute("""
                    INSERT INTO public.projects (title, description, technologies, github_url, live_demo_url)
                    VALUES 
                    ('Crowd Density Counting System', 'A technology-based system designed to monitor and count crowd density using computer vision and deep learning.', 'Python, AI / ML, YOLOv8', 'https://github.com/sahilnawaz257', ''),
                    ('Library Management Software', 'A software solution to manage library books, student records and transactions with automated persistence.', 'Python, SQL, SQLite', 'https://github.com/sahilnawaz257', ''),
                    ('Brand Guideline Audit Tool', 'A tool designed to check brand consistency, typography compliance, and visual palette auditing.', 'HTML, CSS, JavaScript', 'https://github.com/sahilnawaz257', '')
                    ON CONFLICT (title) DO NOTHING;
                """)

            # Seed Education if empty
            cursor.execute("SELECT COUNT(*) as count FROM public.education")
            e_count = cursor.fetchone()["count"]
            if e_count == 0:
                cursor.execute("""
                    INSERT INTO public.education (institution, degree, field, location, start_date, end_date, status, logo_url)
                    VALUES
                    ('JB Group of Institutions of Technology', 'Bachelor of Technology (B.Tech)', 'Computer Science and Engineering (CSE)', 'Dehradun, Uttarakhand, India', '2025', '2029', 'Current (2nd Year)', 'images/jbit-dehradun-logo.png'),
                    ('The Open University', 'Data Analyst Online', 'Computer Science (AI & LangChain RAG)', 'United Kingdom (Online)', 'June 2026', 'July 2029', 'Enrolled / Upcoming', 'images/the-open-university-logo.png')
                    ON CONFLICT (institution) DO NOTHING;
                """)

            # Seed Experience if empty
            cursor.execute("SELECT COUNT(*) as count FROM public.experience")
            exp_count = cursor.fetchone()["count"]
            if exp_count == 0:
                cursor.execute("""
                    INSERT INTO public.experience (company_name, role, duration, description, powered_by)
                    VALUES
                    ('Gymsewa', 'Founder', '2024 – Present', 'Founder of Gymsewa, working on building and developing a business-focused platform. Responsible for product planning, business development, platform strategy, innovation and overall project direction.', 'Bytewave Innovation')
                    ON CONFLICT (company_name) DO NOTHING;
                """)

        else:
            # SQLite Table Initialization
            import sqlite3
            cursor.execute("DROP TABLE IF EXISTS admin_users")
            cursor.execute("DROP TABLE IF EXISTS contacts")

            # Table 1: Contact Messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contact_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    subject TEXT,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table 2: Meeting Bookings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meeting_bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    preferred_date TEXT,
                    preferred_time TEXT,
                    meeting_date TEXT,
                    meeting_time TEXT,
                    status TEXT DEFAULT 'Pending',
                    meeting_link TEXT DEFAULT '',
                    google_meet_link TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table 3: Projects
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    technologies TEXT NOT NULL,
                    github_url TEXT,
                    live_demo_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table 4: Education
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS education (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    institution TEXT NOT NULL,
                    degree TEXT NOT NULL,
                    field TEXT NOT NULL,
                    location TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    logo_url TEXT DEFAULT ''
                )
            """)

            # Table 5: Experience
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experience (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    description TEXT NOT NULL,
                    powered_by TEXT DEFAULT ''
                )
            """)

            # Table 6: Skills
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    category TEXT NOT NULL
                )
            """)

            # Seed authentic Projects if empty
            cursor.execute("SELECT COUNT(*) FROM projects")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                    INSERT INTO projects (title, description, technologies, github_url, live_demo_url)
                    VALUES (?, ?, ?, ?, ?)
                """, [
                    ("Crowd Density Counting System", "A technology-based system designed to monitor and count crowd density.", "Python, AI / ML", "https://github.com/sahilnawaz257", ""),
                    ("Library Management Software", "A software solution to manage library books, student records and transactions.", "Python, SQL", "https://github.com/sahilnawaz257", ""),
                    ("Brand Guideline Audit Tool", "A tool designed to check brand consistency and audit brand guidelines.", "HTML, CSS, JavaScript", "https://github.com/sahilnawaz257", "")
                ])

            # Seed authentic Education if empty
            cursor.execute("SELECT COUNT(*) FROM education")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("""
                    INSERT INTO education (institution, degree, field, location, start_date, end_date, status, logo_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    ('JB Group of Institutions of Technology', 'Bachelor of Technology (B.Tech)', 'Computer Science and Engineering (CSE)', 'Dehradun, Uttarakhand, India', '2025', '2029', 'Current (2nd Year)', 'images/jbit-dehradun-logo.png'),
                    ('The Open University', 'Data Analyst Online', 'Computer Science (AI & LangChain RAG)', 'United Kingdom (Online)', 'June 2026', 'July 2029', 'Enrolled / Upcoming', 'images/the-open-university-logo.png')
                ])

            # Seed authentic Experience if empty
            cursor.execute("SELECT COUNT(*) FROM experience")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO experience (company_name, role, duration, description, powered_by)
                    VALUES (?, ?, ?, ?, ?)
                """, ('Gymsewa', 'Founder', '2024 – Present', 'Founder of Gymsewa, working on building and developing a business-focused platform. Responsible for product planning, business development, platform strategy, innovation and overall project direction.', 'Bytewave Innovation'))

            # Seed authentic Skills if empty
            cursor.execute("SELECT COUNT(*) FROM skills")
            if cursor.fetchone()[0] == 0:
                skills_data = [
                    ('Python', 'Programming Languages'),
                    ('C', 'Programming Languages'),
                    ('C++', 'Programming Languages'),
                    ('Data Structures & Algorithms', 'Programming Languages'),
                    ('HTML5', 'Frontend Engineering'),
                    ('CSS3', 'Frontend Engineering'),
                    ('JavaScript (ES6+)', 'Frontend Engineering'),
                    ('React JS', 'Frontend Engineering'),
                    ('Responsive UI/UX', 'Frontend Engineering'),
                    ('SQL', 'Database Management'),
                    ('SQLite', 'Database Management'),
                    ('Relational Schemas', 'Database Management'),
                    ('Parameterized Queries', 'Database Management'),
                    ('NumPy', 'Data Analysis & AI'),
                    ('Pandas', 'Data Analysis & AI'),
                    ('YOLOv8 Computer Vision', 'Data Analysis & AI'),
                    ('LangChain (RAG)', 'Data Analysis & AI'),
                    ('Git', 'Tools & Workflow'),
                    ('GitHub', 'Tools & Workflow'),
                    ('Flask REST APIs', 'Tools & Workflow'),
                    ('VS Code', 'Tools & Workflow'),
                    ('Product Management', 'Product & Business'),
                    ('Business & Entrepreneurship', 'Product & Business'),
                    ('Leadership & Management', 'Product & Business'),
                    ('Digital & Growth', 'Product & Business')
                ]
                cursor.executemany("INSERT INTO skills (skill_name, category) VALUES (?, ?)", skills_data)
