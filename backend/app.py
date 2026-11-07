"""
Sahil Nawaz Portfolio — Flask Backend Entry Point (Phase 1)
Serves static frontend assets and provides REST API endpoints.
"""

import os
from flask import Flask, send_from_directory, request, make_response, jsonify
from flask_cors import CORS
from routes import api_bp

# Resolve paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "sahil-portfolio-dev-secret-key-2026")

# Enable CORS for cross-origin frontend requests
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register modular API blueprint
app.register_blueprint(api_bp)

# Global CORS headers for preflight and options requests
@app.before_request
def handle_options_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

# Error Handlers returning clean JSON for API requests
@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404
    # Fallback to index.html for frontend routing
    return send_from_directory(FRONTEND_DIR, "index.html"), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"success": False, "error": "Method not allowed for this endpoint"}), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

# Frontend Static Page Routing
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

@app.route("/<path:path>")
def serve_static(path):
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 Sahil Nawaz Portfolio — Flask Backend Running")
    print("  🌐 Website:  http://127.0.0.1:5000")
    print("  🔌 Health:   http://127.0.0.1:5000/api/health")
    print("  📁 Projects: http://127.0.0.1:5000/api/projects")
    print("  ✉️ Contact:  http://127.0.0.1:5000/api/contact")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
