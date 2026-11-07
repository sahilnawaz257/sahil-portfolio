"""
Sahil Nawaz Portfolio — Production-Ready Flask Application (Phase 3)
Features:
- Secure Session Cookies & OWASP Security Headers
- Configurable Origin Filtering (CORS) & CSRF Protection
- SQLite Database Initializer with Automated Seed Management
- Static Frontend Routing, SEO Assets, and Error Handling
"""

import os
import sys
from datetime import timedelta

# Resolve directory paths and ensure backend modules are importable from any CWD
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from flask import Flask, send_from_directory, request, make_response, jsonify
from database import init_db
from routes import api_bp

app = Flask(__name__, static_folder=FRONTEND_DIR)

# ------------------------------------------------------------------------------
# 01. Security & Session Configuration
# ------------------------------------------------------------------------------
IS_PRODUCTION = os.environ.get("FLASK_ENV") == "production" or os.environ.get("PRODUCTION", "").lower() == "true"
ENABLE_HTTPS = os.environ.get("ENABLE_HTTPS", "false").lower() == "true"

# Secret key for signing session cookies
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "sahil-portfolio-dev-secret-key-2026-production-ready"
)

# Secure Session Cookie Flags
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = ENABLE_HTTPS  # True when served over HTTPS
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)

# Trusted origins for CORS
DEFAULT_ORIGINS = "http://127.0.0.1:5000,http://localhost:5000,http://127.0.0.1:5500,http://localhost:3000,http://localhost:8080"
ALLOWED_ORIGINS = {
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",")
    if origin.strip()
}

# ------------------------------------------------------------------------------
# 02. Database Initialization
# ------------------------------------------------------------------------------
init_db()

# ------------------------------------------------------------------------------
# 03. Register Modular REST API Blueprint
# ------------------------------------------------------------------------------
app.register_blueprint(api_bp)

# ------------------------------------------------------------------------------
# 04. CORS Preflight & Security Headers (OWASP Recommended)
# ------------------------------------------------------------------------------
@app.before_request
def handle_options_preflight():
    """Handle CORS OPTIONS preflight requests for allowed origins."""
    if request.method == "OPTIONS":
        response = make_response()
        req_origin = request.headers.get("Origin")

        # Allow if origin is trusted or during local development
        if not req_origin or req_origin in ALLOWED_ORIGINS or not IS_PRODUCTION:
            response.headers["Access-Control-Allow-Origin"] = req_origin or "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, X-CSRF-Token"
            response.headers["Access-Control-Max-Age"] = "3600"
        return response

@app.after_request
def add_security_and_cors_headers(response):
    """Enforce OWASP security headers and trusted CORS on every HTTP response."""
    req_origin = request.headers.get("Origin")

    # Set CORS response headers only if trusted origin or development
    if req_origin and (req_origin in ALLOWED_ORIGINS or not IS_PRODUCTION):
        response.headers["Access-Control-Allow-Origin"] = req_origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, X-CSRF-Token"

    # OWASP Defense-in-Depth Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    # Content Security Policy (allows local assets, Google Fonts, and standard fetch)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' http://127.0.0.1:5000 http://localhost:5000; "
        "frame-ancestors 'self';"
    )

    return response

# ------------------------------------------------------------------------------
# 05. Safe JSON Error Handlers (Prevents Internal Trace Leakage)
# ------------------------------------------------------------------------------
@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({"success": False, "error": "Bad request. Please check your payload."}), 400

@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"success": False, "error": "Unauthorized. Authentication session required."}), 401

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({"success": False, "error": "Forbidden. You do not have permission to access this resource."}), 403

@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "API endpoint not found"}), 404
    return send_from_directory(FRONTEND_DIR, "index.html"), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"success": False, "error": "Method not allowed for this endpoint"}), 405

@app.errorhandler(429)
def too_many_requests_error(error):
    return jsonify({"success": False, "error": "Too many requests. Please wait a moment before trying again."}), 429

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"success": False, "error": "Internal server error. Please try again later."}), 500

# ------------------------------------------------------------------------------
# 06. Frontend Static Page & Asset Routing
# ------------------------------------------------------------------------------
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/about")
@app.route("/about.html")
def serve_about():
    return send_from_directory(FRONTEND_DIR, "about.html")

@app.route("/projects")
@app.route("/projects.html")
def serve_projects():
    return send_from_directory(FRONTEND_DIR, "projects.html")

@app.route("/admin")
@app.route("/admin.html")
def serve_admin():
    return send_from_directory(FRONTEND_DIR, "admin.html")

@app.route("/favicon.ico")
@app.route("/favicon.svg")
def serve_favicon():
    return send_from_directory(FRONTEND_DIR, "favicon.svg", mimetype="image/svg+xml")

@app.route("/<path:path>")
def serve_static(path):
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ------------------------------------------------------------------------------
# Server Runner
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    debug = not IS_PRODUCTION

    print("=" * 65)
    print("  🚀 Sahil Nawaz Portfolio — Production Backend (Phase 3)")
    print(f"  🌐 Website:        http://{host}:{port}")
    print(f"  🔐 Admin Center:   http://{host}:{port}/admin")
    print(f"  🔌 Health API:     http://{host}:{port}/api/health")
    print(f"  📁 Projects API:   http://{host}:{port}/api/projects")
    print(f"  ✉️ Contact API:    http://{host}:{port}/api/contact")
    print(f"  🛡️ Security Mode:  {'PRODUCTION' if IS_PRODUCTION else 'DEVELOPMENT'}")
    print("=" * 65)
    app.run(host=host, port=port, debug=debug)
