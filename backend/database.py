"""
Sahil Nawaz Portfolio — SQLite Database Module
Manages connection, table creation for contact messages & projects, and authentic project seeds.
"""

import os
import sqlite3

# Resolve database directory relative to backend
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
DB_PATH = os.path.join(DATABASE_DIR, "portfolio.db")

def get_db_connection():
    """Return an active connection to the SQLite database with Row factory."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize SQLite database tables and seed authentic project records.
    Clean up any legacy unused admin tables.
    """
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Permanently remove any legacy admin or unused tables
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

    # Table 2: Projects
    cursor.execute("PRAGMA table_info(projects)")
    existing_cols = [row["name"] for row in cursor.fetchall()]
    if existing_cols and "technologies" not in existing_cols:
        cursor.execute("DROP TABLE projects")

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

    # Table 3: Meeting Bookings (Google Meet Scheduling)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            purpose TEXT NOT NULL,
            meeting_date TEXT NOT NULL,
            meeting_time TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            google_meet_link TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed Authentic Projects if table is empty
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        seed_projects = [
            (
                "Crowd Density Counting System",
                "A technology-based system designed to monitor and count crowd density.",
                "Python, AI / ML",
                "https://github.com/sahilnawaz257",
                ""
            ),
            (
                "Library Management Software",
                "A software solution to manage library books, student records and transactions.",
                "Python, SQL",
                "https://github.com/sahilnawaz257",
                ""
            ),
            (
                "Brand Guideline Audit Tool",
                "A tool designed to check brand consistency and audit brand guidelines.",
                "HTML, CSS, JavaScript",
                "https://github.com/sahilnawaz257",
                ""
            )
        ]
        cursor.executemany("""
            INSERT INTO projects (title, description, technologies, github_url, live_demo_url)
            VALUES (?, ?, ?, ?, ?)
        """, seed_projects)

    conn.commit()
    conn.close()
