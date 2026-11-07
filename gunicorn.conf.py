import os

# Render port binding configuration
# Automatically binds to 0.0.0.0:$PORT as required by Render
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"

workers = 2
threads = 4
timeout = 120
accesslog = "-"
errorlog = "-"
