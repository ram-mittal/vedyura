import os
import sys

# Add project root to sys.path so app and its modules can be loaded
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Export app for Vercel Serverless WSGI
app.debug = False
