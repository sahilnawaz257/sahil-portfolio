# Sahil Nawaz — Forward Deployed Developer Portfolio

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Backend-Flask-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![Security](https://img.shields.io/badge/Security-OWASP%20Hardened-coral.svg)](#security--architecture)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](#)

A full-stack, responsive developer portfolio engineered with a **Python Flask backend**, **SQLite database persistence**, and an interactive **vanilla JavaScript & semantic HTML5/CSS3 frontend**. Styled in a modern warm coral-pink aesthetic, showcasing authentic projects across **Artificial Intelligence, Computer Vision, and Software Engineering**.

---

## 🌟 Key Highlights & Capabilities

- **Modern Coral-Pink Aesthetic:** Responsive design built with CSS custom properties, fluid typography (`DM Sans` & `Manrope`), CSS illustrations, and mobile drawer navigation.
- **Laptop & Desktop Optimized:** Tuned viewport heights and responsive breakpoints ensuring above-the-fold content and highlight metrics fit on any laptop screen.
- **Dynamic Projects Showcase:** Fetches project records dynamically from SQLite with automatic progressive enhancement fallbacks for offline or static hosting.
- **Persistent Inquiries Storage:** Visitor contact form submissions are validated, sanitized against XSS, and stored directly in SQLite with assigned reference IDs.
- **Defense-in-Depth Security:** Sliding window IP rate limiting, OWASP recommended HTTP security headers, and 100% parameterized SQL queries.

---

## 📁 Project Architecture

```text
Sahil-Portfolio/
│
├── frontend/
│   ├── index.html          # Main landing page (Hero, About, Skills, Projects, Education, Contact, Footer)
│   ├── about.html          # In-depth biography, academic background, and technical journey
│   ├── projects.html       # Portfolio showcase with category filtering
│   ├── favicon.svg         # Vector favicon badge (</>)
│   ├── css/
│   │   └── style.css       # Responsive custom CSS (coral-pink palette, typography, animations)
│   ├── js/
│   │   └── script.js       # Dynamic projects loader, scrollspy, contact API handler, mobile drawer
│   └── images/
│       └── sahil-nawaz.jpg # Profile portrait photograph
│
├── backend/
│   ├── app.py              # Flask server, security middleware, static routing, and error handlers
│   ├── database.py         # SQLite connection manager, automated table migration, and seed logic
│   ├── models.py           # ContactMessage and Project data access models
│   ├── routes.py           # Modular REST API endpoints with rate limit protection
│   └── requirements.txt    # Python dependencies (Flask, flask-cors, Werkzeug, gunicorn)
│
├── database/
│   ├── .gitkeep            # Version control placeholder
│   └── portfolio.db        # SQLite database (auto-generated on app startup)
│
├── .env.example            # Template for environment configuration & secrets
├── .gitignore              # Production-grade git exclusions
└── README.md               # Complete project documentation and deployment guide
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed
- **Git** installed

### 2. Clone Repository & Setup Environment

```powershell
# Clone the repository
git clone https://github.com/sahilnawaz257/sahil-portfolio.git
cd sahil-portfolio

# Create and activate a Python virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\activate

# On macOS / Linux:
# python3 -m venv .venv
# source .venv/bin/activate
```

### 3. Install Dependencies

```powershell
pip install -r backend/requirements.txt
```

### 4. Launch Application Server

```powershell
python backend/app.py
```

### 5. Access in Browser

- 🌐 **Portfolio Website:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- 🔌 **API Health Status:** [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health)
- 📁 **Projects API:** [http://127.0.0.1:5000/api/projects](http://127.0.0.1:5000/api/projects)

---

## 🔌 RESTful API Reference

| Method | Endpoint | Description | Status Codes |
|---|---|---|:---:|
| `GET` | `/api/health` | System health check and current status | `200` |
| `GET` | `/api/projects` | Retrieve all dynamic portfolio projects | `200`, `500` |
| `GET` | `/api/projects/<id>` | Retrieve details of a single project | `200`, `404` |
| `GET` | `/api/education` | Retrieve formal academic background records | `200`, `500` |
| `GET` | `/api/experience` | Retrieve professional venture & leadership records | `200`, `500` |
| `GET` | `/api/skills` | Retrieve technical & business skill inventory | `200`, `500` |
| `POST` | `/api/contact` | Submit contact inquiry to database & trigger email alert | `201`, `400`, `429` |
| `POST` | `/api/meetings/book` | Schedule Google Meet appointment (duplicate & past-date validation) | `201`, `400`, `409`, `429` |
| `GET` | `/api/meetings/status/<id>` | Retrieve real-time meeting booking status and Google Meet link | `200`, `404` |

---

## 🗄️ Supabase PostgreSQL Integration & Migration

The portfolio supports a **dual-engine database architecture**:
- **Production:** Supabase PostgreSQL with automated TLS/SSL encryption and Row Level Security (RLS).
- **Development / Fallback:** Local SQLite (`database/portfolio.db`) ensuring immediate out-of-the-box local execution if remote credentials are not set.

### 1. Database Tables Overview
The following 6 tables are managed in Supabase PostgreSQL:
1. **`contact_messages`**: Visitor inquiries with full name, email, subject, message, and timestamp.
2. **`meeting_bookings`**: Google Meet appointment scheduling with name, email, purpose, preferred date, preferred time, status, and meeting link.
3. **`projects`**: Authentic production AI, vision, and full-stack software systems.
4. **`education`**: Verified academic credentials (JBIT Dehradun & The Open University).
5. **`experience`**: Venture track record (Founder — Gymsewa, Powered by Bytewave Innovation).
6. **`skills`**: Categorized technical, analytical, and product/business capabilities.

### 2. Row Level Security (RLS) Configuration
Strict visitor privacy and zero-admin exposure policies:
- **`contact_messages`**: Public visitors can `INSERT` only. Public `SELECT` is blocked to prevent data scraping.
- **`meeting_bookings`**: Public visitors can `INSERT` only. Public scraping is blocked.
- **`projects`, `education`, `experience`, `skills`**: Public read access (`SELECT`) enabled for all portfolio visitors. Write permissions are restricted to the server-side `service_role`.

### 3. Step-by-Step Supabase Setup
1. Log in to your [Supabase Dashboard](https://supabase.com/dashboard) and create or select your project.
2. Navigate to the **SQL Editor** in the left sidebar.
3. Open [`database/supabase_schema.sql`](database/supabase_schema.sql), copy its complete contents, paste into the SQL Editor, and click **Run**.
4. In Supabase, go to **Project Settings** -> **Database** and copy your **URI Connection string** (Transaction Pooler or Direct).
5. Copy `.env.example` to `.env` and set:
   ```env
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
   SUPABASE_ANON_KEY=your-supabase-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
   PGSSLMODE=require
   ```
6. *(Optional)* To migrate existing SQLite records into your new Supabase database, run:
   ```powershell
   python database/supabase_migration_from_sqlite.py
   ```

---

## 🛡️ Security & Architecture

The application implements enterprise-grade security practices aligned with the **OWASP Top 10**:

1. **SQL Injection Prevention:**
   All SQLite queries in [`database.py`](file:///c:/Users/Adil%20nawaz/Music/Protiflio/backend/database.py) and [`models.py`](file:///c:/Users/Adil%20nawaz/Music/Protiflio/backend/models.py) use 100% parameterized binding (`?`). Zero dynamic string concatenation.
2. **Session Cookie Hardening:**
   Cookies are configured with `HttpOnly=True` (mitigates XSS cookie theft), `SameSite=Lax`, and `Secure=True` when running under HTTPS.
3. **Spam & Flooding Throttling:**
   In-memory sliding window rate limiters restrict `/api/contact` to 8 submissions/min per IP address.
4. **Cross-Site Scripting (XSS) Sanitization:**
   All user submissions from contact forms are HTML-escaped using Python's `html.escape()` prior to storage and rendering.
5. **OWASP HTTP Security Headers:**
   Every HTTP response is fortified with:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: SAMEORIGIN`
   - `X-XSS-Protection: 1; mode=block`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Content-Security-Policy`
6. **Safe Error Handling:**
   Standardized JSON error handlers (400, 404, 405, 429, 500) prevent internal Python stack traces from leaking to clients.

---

## 🚀 Live Production Deployment Guide

### Option 1: Render.com / Railway
1. Push your repository to GitHub.
2. Create a new **Web Service** pointing to your repository.
3. Configure build and start settings:
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `gunicorn --chdir backend app:app -b 0.0.0.0:$PORT`
4. Set Environment Variables in dashboard:
   - `SECRET_KEY`: A random 32-character string
   - `FLASK_ENV`: `production`
   - `ENABLE_HTTPS`: `true`

### Option 2: PythonAnywhere
1. Clone the repository into your PythonAnywhere console.
2. Create a Python 3.10+ virtualenv and run `pip install -r backend/requirements.txt`.
3. In the **Web** tab, configure the WSGI configuration file:
   ```python
   import sys
   path = '/home/yourusername/sahil-portfolio/backend'
   if path not in sys.path:
       sys.path.insert(0, path)
   from app import app as application
   ```
4. Reload the web app.

---

## 👤 Developer Profile

- **Name:** Sahil Nawaz
- **Role:** Forward Deployed Developer & AI Enthusiast
- **Venture:** Founder, Gymsewa (Powered by Bytewave Innovation, 2024–Present)
- **Education:** B.Tech in Computer Science and Engineering, JB Group of Institutions of Technology, Dehradun, Uttarakhand (2025–2029) & Data Analytics at The Open University (2026–2029)
- **Skills:** Python, C, C++, HTML5, CSS3, JavaScript, React JS, SQL, SQLite, NumPy, Pandas, YOLOv8, LangChain (RAG), Product Management, Business & Entrepreneurship, Leadership & Management, Digital & Growth
- **Email:** [sahilnawaz257@gmail.com](mailto:sahilnawaz257@gmail.com)
- **GitHub:** [github.com/sahilnawaz257](https://github.com/sahilnawaz257)
- **LinkedIn:** [Ali Sahil Nawaz](https://www.linkedin.com/in/ali-sahil-nawaz-622b58213/)
- **LeetCode:** [Alisahilnawaz](https://leetcode.com/u/Alisahilnawaz/)

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
