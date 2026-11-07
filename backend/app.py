import os
from flask import Flask, send_from_directory, request, make_response
from database import init_db
from routes import api_bp

# Resolve paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)

# Initialize SQLite database
init_db()

# Register API routes
app.register_blueprint(api_bp)

# Enable CORS for local development and cross-origin frontend requests
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

# Serve Frontend Pages & Assets directly from Flask
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
@app.route("/messages")
def serve_admin():
    return send_from_directory(FRONTEND_DIR, "admin.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 Sahil Nawaz Portfolio Server Running")
    print("  🌐 Website:  http://127.0.0.1:5000")
    print("  🔌 API:      http://127.0.0.1:5000/api/health")
    print("  📁 Frontend: " + FRONTEND_DIR)
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)

