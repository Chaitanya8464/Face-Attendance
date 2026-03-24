import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.app import app

# Vercel serverless handler
def handler(request):
    return app(request.environ, lambda *args: None)
