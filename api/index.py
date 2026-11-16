import os
import sys
import traceback

# Add project root to sys.path so app and its modules can be loaded
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app import app
    app.debug = False
except Exception as e:
    from flask import Flask
    err_tb = traceback.format_exc()
    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def error_handler(path):
        return f"""
        <html>
        <head><title>Vedyura Initialization Error</title></head>
        <body style="font-family: monospace; padding: 20px; background: #1a1a1a; color: #ff5555;">
            <h2>Serverless Startup Error</h2>
            <pre style="background: #2a2a2a; color: #ffffff; padding: 16px; border-radius: 8px; overflow-x: auto;">{err_tb}</pre>
        </body>
        </html>
        """, 500
