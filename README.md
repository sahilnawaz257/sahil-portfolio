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
- **Dynamic Projects Showcase:** Fetches project records dynamically from SQLite with automatic progressive enhancement fallbacks for offline or static hosting.
- **Persistent Inquiries Inbox:** Visitor contact form submissions are validated, sanitized against XSS, and stored in SQLite with assigned reference IDs.
- **Protected Admin Dashboard:** Session-authenticated command center for viewing contact messages, replying via email, and performing full CRUD on portfolio projects.
- **Defense-in-Depth Security:** CSRF protection with custom tokens, sliding window IP rate limiting, OWASP recommended HTTP security headers, PBKDF2 password hashing, and 100% parameterized SQL queries.

---

## 📁 Project Architecture

```text
Sahil-Portfolio/
│
├── frontend/
│   ├── index.html          # Main landing page (Hero, About, Skills, Projects, Education, Contact, Footer)
│   ├── about.html          # In-depth biography, academic background, and technical journey
│   ├── projects.html       # Portfolio showcase with category filtering
│   ├── admin.html          # Protected Admin Dashboard (Inbox & Project Management)
│   ├── favicon.svg         # Vector favicon badge (</>)
│   ├── css/
│   │   └── style.css       # Responsive custom CSS (coral-pink palette, typography, animations)
│   └── js/
│       └── script.js       # Dynamic projects loader, scrollspy, contact API handler, mobile drawer
│
├── backend/
│   ├── app.py              # Flask server, security middleware, static routing, and error handlers
│   ├── database.py         # SQLite connection manager, automated table migration, and seed logic
│   ├── models.py           # ContactMessage, Project, and AdminUser data access models
│   ├── routes.py           # Modular REST API endpoints with CSRF & rate limit protection
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

### 4. Configure Environment Variables (Optional for Local Dev)

Copy the example environment file:
```powershell
copy .env.example .env
```
*(The backend defaults to safe local development values if `.env` is omitted).*

### 5. Launch Application Server

```powershell
python backend/app.py
```

### 6. Access in Browser

- 🌐 **Portfolio Website:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- 🔐 **Admin Dashboard:** [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)
- 🔌 **API Health Status:** [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health)
- 📁 **Projects API:** [http://127.0.0.1:5000/api/projects](http://127.0.0.1:5000/api/projects)

> **Default Admin Credentials (Local Verification):**
> - **Username:** `admin`
> - **Password:** `SahilAdmin2026!` *(Change in `.env` before production deployment)*

---

## 🔌 RESTful API Reference

| Method | Endpoint | Auth Required | Description | Status Codes |
|---|---|:---:|---|:---:|
| `GET` | `/api/health` | No | System health check and current phase | `200` |
| `GET` | `/api/projects` | No | Retrieve all dynamic portfolio projects from SQLite | `200`, `500` |
| `GET` | `/api/projects/<id>` | No | Retrieve details of a single project | `200`, `404` |
| `POST` | `/api/contact` | No (Rate Limited) | Submit contact inquiry to SQLite database | `201`, `400`, `429` |
| `POST` | `/api/admin/login` | No (Rate Limited) | Verify admin credentials; issues session & CSRF token | `200`, `400`, `401`, `429` |
| `POST` | `/api/admin/logout` | Yes | Invalidate admin session and clear CSRF token | `200` |
| `GET` | `/api/admin/status` | No | Check active authentication status and retrieve CSRF token | `200` |
| `GET` | `/api/admin/messages` | Yes | Retrieve all contact messages stored in SQLite | `200`, `401` |
| `DELETE` | `/api/admin/messages/<id>` | Yes + CSRF | Permanently delete a contact message | `200`, `401`, `403`, `404` |
| `POST` | `/api/admin/projects` | Yes + CSRF | Add a new project to the database | `201`, `400`, `401`, `403` |
| `PUT` | `/api/admin/projects/<id>` | Yes + CSRF | Update an existing project record | `200`, `400`, `401`, `403`, `404` |
| `DELETE` | `/api/admin/projects/<id>` | Yes + CSRF | Remove a project from the database | `200`, `401`, `403`, `404` |

---

## 🛡️ Security & Architecture (Phase 3)

The application implements enterprise-grade security practices aligned with the **OWASP Top 10**:

1. **SQL Injection Prevention:**
   All SQLite queries in [`database.py`](file:///c:/Users/Adil%20nawaz/Music/Protiflio/backend/database.py) and [`models.py`](file:///c:/Users/Adil%20nawaz/Music/Protiflio/backend/models.py) use 100% parameterized binding (`?`). Zero dynamic string concatenation.
2. **Cross-Site Request Forgery (CSRF) Protection:**
   State-mutating administrative actions (`POST`, `PUT`, `DELETE`) require a cryptographically generated anti-CSRF token delivered in the `X-CSRF-Token` header and verified with `secrets.compare_digest()`.
3. **Session Cookie Hardening:**
   Session cookies are configured with `HttpOnly=True` (mitigates XSS cookie theft), `SameSite=Lax`, and `Secure=True` when running under HTTPS.
4. **Brute Force & Spam Throttling:**
   In-memory sliding window rate limiters restrict `/api/contact` to 8 submissions/min and `/api/admin/login` to 5 attempts/min per IP address.
5. **Cross-Site Scripting (XSS) Sanitization:**
   All user submissions from contact forms and project administration are HTML-escaped using Python's `html.escape()` prior to storage and rendering.
6. **OWASP HTTP Security Headers:**
   Every HTTP response is fortified with:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: SAMEORIGIN`
   - `X-XSS-Protection: 1; mode=block`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Content-Security-Policy`
7. **Safe Error Handling:**
   Standardized JSON error handlers (400, 401, 403, 404, 405, 429, 500) prevent internal Python stack traces from leaking to clients.

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
   - `ADMIN_USERNAME`: Your custom admin username
   - `ADMIN_PASSWORD`: Your strong admin password
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
- **Education:** B.Tech in Computer Science and Engineering, J.B. Institute of Engineering & Technology (2025–Present)
- **Email:** [sahilnawaz257@gmail.com](mailto:sahilnawaz257@gmail.com)
- **GitHub:** [github.com/sahilnawaz257](https://github.com/sahilnawaz257)
- **LinkedIn:** [Ali Sahil Nawaz](https://www.linkedin.com/in/ali-sahil-nawaz-622b58213/)
- **LeetCode:** [Alisahilnawaz](https://leetcode.com/u/Alisahilnawaz/)

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
