import os

# Render port binding configuration
# Automatically binds to 0.0.0.0:$PORT as required by Render
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"

# High performance multi-threaded worker model optimized for fast responses
workers = 2
threads = 4
worker_class = "gthread"
keepalive = 10
timeout = 120
preload_app = True
accesslog = "-"
errorlog = "-"
