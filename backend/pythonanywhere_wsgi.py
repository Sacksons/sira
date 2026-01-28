"""
PythonAnywhere WSGI Configuration
Copy this file to /var/www/<username>_pythonanywhere_com_wsgi.py
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/<username>/sira/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://<username>:<password>@<username>-<dbname>.postgres.pythonanywhere-services.com/<dbname>'
os.environ['SECRET_KEY'] = 'your-production-secret-key-change-this'
os.environ['DEBUG'] = 'False'
os.environ['LOG_LEVEL'] = 'WARNING'

# Import the FastAPI app
from app.main import app

# PythonAnywhere uses WSGI, so we need to wrap FastAPI
# Option 1: Use uvicorn's ASGI to WSGI adapter (recommended)
# Install: pip install a]sgi-wsgi-translator

# For now, use the app directly
application = app
