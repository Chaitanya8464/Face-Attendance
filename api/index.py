import sys
import os

# Set up paths for Vercel
vercel_path = os.path.dirname(__file__)
project_root = os.path.dirname(vercel_path)

# Add project root to Python path
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

# Set environment variables for Vercel
os.environ['VERCEL'] = '1'
os.environ['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'production')
os.environ['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vercel-dev-key')

# Import the Flask app
from backend.app.app import app

# Export for Vercel serverless
__all__ = ['app']
