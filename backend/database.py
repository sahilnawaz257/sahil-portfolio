import os
import sqlite3
from datetime import datetime

# Resolve database path relative to this backend module
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
DB_PATH = os.path.join(DATABASE_DIR, "portfolio.db")

def get_db_connection():
    """Return a connection to the SQLite database with row factory enabled."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables and seed initial project data if needed."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create contacts/messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'unread'
        )
    """)

    # Create projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            badge TEXT,
            summary TEXT NOT NULL,
            description TEXT NOT NULL,
            tech_stack TEXT NOT NULL,
            github_url TEXT,
            live_url TEXT,
            featured INTEGER DEFAULT 0,
            metric TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if projects need seeding
    cursor.execute("SELECT COUNT(*) FROM projects")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_projects = [
            (
                "Crowd Density & Anomaly Detection Surveillance System",
                "crowd-density-detection",
                "ai-cv",
                "AI & Computer Vision",
                "An intelligent real-time computer vision platform for human detection, ByteTrack tracking, 2D Gaussian heatmaps, and threat anomaly detection.",
                "Engineered with Ultralytics YOLOv8n and ByteTrack, this system processes multi-camera feeds at 30 FPS. It features 4-quadrant spatial density estimation, virtual bi-directional tripwire counting, OpenCV Jet thermal heatmaps, and rule-based anomaly detection for sudden surges, stampede risks, and bottleneck congestion. Complete with a FastAPI ASGI backend, WebSockets, and a React/Vite dark-navy surveillance console (24/24 Pytests passing).",
                "Python 3.14, YOLOv8n, ByteTrack, OpenCV, PyTorch, FastAPI, WebSockets, React.js, Tailwind CSS",
                "https://github.com/sahilnawaz257",
                "#",
                1,
                "1,248 Detections / Min"
            ),
            (
                "StudentSync: QR-Based Library & Attendance System",
                "studentsync-library",
                "software",
                "Full-Stack Campus Software",
                "A digital campus automation platform modernizing library attendance and inventory with dynamic QR codes and analytics.",
                "Built with a React.js client and an Express/Prisma ORM backend. Features student digital authentication, instantaneous QR code scanning for touchless library entry/exit, automated overdue fine accounting, book catalog search, and real-time administrative reporting dashboards.",
                "React.js, Node.js, Express, Prisma ORM, PostgreSQL, QR Authentication, Tailwind CSS",
                "https://github.com/sahilnawaz257",
                "#",
                1,
                "99.4% Scan Reliability"
            ),
            (
                "Brand Guideline Audit Tool",
                "brand-guideline-audit",
                "product",
                "Product & Design Tool",
                "An automated linter and compliance auditor verifying typography scales, color contrast, and design tokens.",
                "Allows design and engineering teams to crawl web applications to identify brand inconsistencies, non-standard palette deviations, and WCAG AA/AAA accessibility contrast failures, generating actionable audit reports with visual health scoring.",
                "JavaScript, CSS AST Parser, Python, WCAG Scoring, Design Tokens",
                "https://github.com/sahilnawaz257",
                "#",
                1,
                "100% Brand Consistency"
            ),
            (
                "Portfolio RESTful Backend API & Admin Console",
                "portfolio-backend-api",
                "backend",
                "Backend Engineering",
                "High-performance REST API and message store powering dynamic inquiries, project discovery, and admin management.",
                "Built with Flask and SQLite, featuring modular Blueprints, CORS preflight handling, parameterized SQL security, and a dedicated responsive admin management panel for message workflows.",
                "Python, Flask, SQLite3, REST API, CORS Architecture",
                "https://github.com/sahilnawaz257",
                "#",
                0,
                "< 20ms Latency"
            )
        ]

        cursor.executemany("""
            INSERT INTO projects (
                title, slug, category, badge, summary, description,
                tech_stack, github_url, live_url, featured, metric
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_projects)

        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DB_PATH}")

