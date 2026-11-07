"""
Sahil Nawaz Portfolio — Database Module (Supabase PostgreSQL & SQLite Engine)
Supports:
1. Supabase PostgreSQL via DATABASE_URL or SUPABASE_DB_URL (using psycopg2 with SSL)
2. Supabase Client via SUPABASE_URL + SUPABASE_KEY / SUPABASE_SERVICE_ROLE_KEY
3. Local SQLite fallback (database/portfolio.db) when remote credentials are not configured

Features:
- Zero Admin Dashboard / Zero Admin Tables
- 100% Parameterized Queries for SQL Injection Defense
- Row Level Security (RLS) Ready for Supabase PostgreSQL
- Automatic Schema Creation & Authentic Data Seeding
"""

import os
import re
import sqlite3

# Try loading environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
DB_PATH = os.path.join(DATABASE_DIR, "portfolio.db")

# PostgreSQL / Supabase Configuration
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL") or ""
SUPABASE_URL = os.environ.get("SUPABASE_URL") or ""
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or ""

_SUPABASE_CLIENT = None

def is_postgres():
    """Return True if a PostgreSQL / Supabase connection URL is configured."""
    return bool(DATABASE_URL and DATABASE_URL.startswith(("postgres://", "postgresql://")))

def get_supabase_client():
    """
    Return initialized Supabase REST client if SUPABASE_URL and key are available.
    Never exposes service role key to frontend.
    """
    global _SUPABASE_CLIENT
    if _SUPABASE_CLIENT is not None:
        return _SUPABASE_CLIENT

    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client, Client
            _SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_KEY)
            return _SUPABASE_CLIENT
        except Exception as e:
            print(f"[SUPABASE CLIENT WARNING] Failed to initialize Supabase client: {e}")
            return None
    return None

def get_db_connection():
    """
    Return an active database connection.
    Connects to Supabase PostgreSQL when DATABASE_URL is configured,
    or falls back to local SQLite database.
    """
    if is_postgres():
        import psycopg2
        from psycopg2.extras import RealDictCursor

        # Supabase requires SSL encryption for pooled / direct connections
        conn = psycopg2.connect(
            DATABASE_URL,
            sslmode=os.environ.get("PGSSLMODE", "require"),
            cursor_factory=RealDictCursor
        )
        return conn
    else:
        os.makedirs(DATABASE_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

def adapt_query(query):
    """
    Translate parameterized query placeholders:
    Uses %s for PostgreSQL and ? for SQLite.
    """
    if is_postgres():
        return query
    # Convert %s placeholder to ? for SQLite
    return re.sub(r'%s', '?', query)

def execute_query(query, params=(), fetch="none", commit=False):
    """
    Execute a parameterized SQL query across PostgreSQL or SQLite.
    fetch: 'none', 'one', or 'all'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    adapted_sql = adapt_query(query)

    try:
        cursor.execute(adapted_sql, params)
        result = None
        if fetch == "one":
            row = cursor.fetchone()
            result = dict(row) if row else None
        elif fetch == "all":
            rows = cursor.fetchall()
            result = [dict(r) for r in rows]

        if commit:
            conn.commit()
        return result
    finally:
        cursor.close()
        conn.close()

def insert_and_get_id(query, params=(), id_col="id"):
    """
    Execute an INSERT statement using parameterized values and return the new primary key ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if is_postgres():
            # In PostgreSQL, append RETURNING id if not already in query
            if not re.search(r'\breturning\b', query, re.I):
                pg_query = f"{query.rstrip(';')} RETURNING {id_col}"
            else:
                pg_query = query
            cursor.execute(pg_query, params)
            row = cursor.fetchone()
            conn.commit()
            return row[id_col] if isinstance(row, dict) else row[0]
        else:
            sqlite_query = adapt_query(query)
            cursor.execute(sqlite_query, params)
            new_id = cursor.lastrowid
            conn.commit()
            return new_id
    finally:
        cursor.close()
        conn.close()

def init_db():
    """
    Initialize database schema (PostgreSQL or SQLite), remove legacy admin tables,
    and seed authentic portfolio data if empty.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if is_postgres():
            # Apply PostgreSQL schema with UUID and BIGINT identity keys
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.contact_messages (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    subject TEXT DEFAULT '',
                    message TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS public.meeting_bookings (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    preferred_date DATE NOT NULL,
                    preferred_time TEXT NOT NULL,
                    status TEXT DEFAULT 'Pending' NOT NULL,
                    meeting_link TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS public.projects (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    technologies TEXT NOT NULL,
                    github_url TEXT DEFAULT '',
                    live_demo_url TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS public.education (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    institution TEXT NOT NULL,
                    degree TEXT NOT NULL,
                    field TEXT NOT NULL,
                    location TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    logo_url TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS public.experience (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    description TEXT NOT NULL,
                    powered_by TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS public.skills (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    skill_name TEXT NOT NULL,
                    category TEXT NOT NULL
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
                """)

            # Seed Experience if empty
            cursor.execute("SELECT COUNT(*) as count FROM public.experience")
            exp_count = cursor.fetchone()["count"]
            if exp_count == 0:
                cursor.execute("""
                    INSERT INTO public.experience (company_name, role, duration, description, powered_by)
                    VALUES
                    ('Gymsewa', 'Founder', '2024 – Present', 'Founder of Gymsewa, working on building and developing a business-focused platform. Responsible for product planning, business development, platform strategy, innovation and overall project direction.', 'Bytewave Innovation')
                """)

            conn.commit()

        else:
            # SQLite Table Initialization
            os.makedirs(DATABASE_DIR, exist_ok=True)
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

            conn.commit()

    finally:
        cursor.close()
        conn.close()
