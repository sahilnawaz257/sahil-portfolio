# Sahil Nawaz — Forward Deployed Developer Portfolio

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Backend-Flask-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](#)

A full-stack, responsive developer portfolio showcasing projects in **Artificial Intelligence, Computer Vision (YOLOv8), Full-Stack Systems, and Product Engineering**.

---

## 📁 Project Structure

```text
Sahil-Portfolio/
│
├── frontend/
│   ├── index.html          # Main landing page (Hero, Skills, Highlights, Featured Projects)
│   ├── about.html          # In-depth story, engineering philosophy, academic journey
│   ├── projects.html       # Categorized portfolio projects with interactive filters
│   ├── css/
│   │   └── style.css       # Responsive custom CSS (warm peach/coral modern palette)
│   ├── js/
│   │   └── script.js       # Dynamic active navigation, mobile toggle, contact API handler
│   └── images/
│       ├── hero.png        # Sahil Nawaz profile & hero portrait
│       └── profile.png     # Avatar image asset
│
├── backend/
│   ├── app.py              # Main Flask server with CORS & static file router
│   ├── database.py         # SQLite connection helpers & automated seed script
│   ├── models.py           # Contact and Project data models
│   ├── routes.py           # RESTful API endpoints for projects & contact inquiries
│   └── requirements.txt    # Python dependencies (Flask, flask-cors)
│
├── database/
│   ├── .gitkeep            # Version control placeholder
│   └── portfolio.db        # Auto-generated SQLite database
│
└── README.md               # Documentation and setup guide
```

---

## ⚡ Quick Start Guide

### Option 1: Run Full-Stack App with Python (Recommended)

The Flask backend is configured to serve both the REST API and the frontend static files simultaneously:

1. **Open PowerShell / Terminal** in the project directory:
   ```powershell
   cd "C:\Users\Adil nawaz\Music\Protiflio"
   ```

2. **(Optional) Create & activate a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r backend/requirements.txt
   ```

4. **Start the server**:
   ```powershell
   python backend/app.py
   ```

5. **Visit the application in your browser**:
   - 🌐 **Website**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - 🔌 **API Health**: [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health)
   - 📂 **Projects API**: [http://127.0.0.1:5000/api/projects](http://127.0.0.1:5000/api/projects)

---

### Option 2: Run Frontend Only (Static / Live Server)

If you just want to preview or customize the design:
- Open `frontend/index.html` directly in any web browser, or
- Right-click `frontend/index.html` in VS Code and choose **"Open with Live Server"**.
- *Note:* The contact form seamlessly falls back to `mailto:` if the Flask backend is not running.

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description | Sample Response / Payload |
|---|---|---|---|
| `GET` | `/api/health` | Service health status | `{"status": "healthy"}` |
| `GET` | `/api/projects` | Fetch all projects (supports `?category=` filter) | `{"success": true, "projects": [...]}` |
| `GET` | `/api/projects/<id>` | Fetch a single project by ID | `{"success": true, "project": {...}}` |
| `POST` | `/api/contact` | Submit contact inquiry (saved to SQLite) | `{"name": "...", "email": "...", "message": "..."}` |
| `GET` | `/api/messages` | View all submitted contact messages | `{"success": true, "messages": [...]}` |

---

## 🛠️ Tech Stack & Key Features

- **Frontend**: HTML5, semantic markup, responsive vanilla CSS3 with custom variables, vanilla JavaScript ES6+.
- **Backend**: Python 3.14 / Flask 3.1, Blueprint-based modular routing, CORS-enabled for flexible cross-origin deployment.
- **Database**: SQLite3 with auto-initialization and seed data.
- **Visual Design**: Typography pairing (**DM Sans** and **Manrope**), custom illustration badges, accessible WCAG contrast.

---

## 👤 Developer Profile

- **Name**: Sahil Nawaz
- **Title**: Forward Deployed Developer / AI Enthusiast
- **Education**: B.Tech in Computer Science & Engineering, JBIET (2025 – Present)
- **Email**: [sahilnawaz257@gmail.com](mailto:sahilnawaz257@gmail.com)
- **GitHub**: [github.com/sahilnawaz257](https://github.com/sahilnawaz257)
- **LinkedIn**: [Ali Sahil Nawaz](https://www.linkedin.com/in/ali-sahil-nawaz-622b58213/)

