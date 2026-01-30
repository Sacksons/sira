"""
PythonAnywhere WSGI Configuration for SIRA Platform

SETUP INSTRUCTIONS:
1. Copy this content to: /var/www/<username>_pythonanywhere_com_wsgi.py
2. Update <username> with your PythonAnywhere username
3. Update the DATABASE_URL with your PostgreSQL credentials
4. Set a strong SECRET_KEY for production
"""

import sys
import os

# =============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# =============================================================================
PYTHONANYWHERE_USERNAME = '<username>'  # Your PythonAnywhere username
DATABASE_NAME = 'sira'                   # Your PostgreSQL database name
DATABASE_PASSWORD = '<db_password>'      # Your database password
SECRET_KEY = 'change-this-to-a-strong-random-secret-key-in-production'

# =============================================================================
# PATH SETUP
# =============================================================================
project_home = f'/home/{PYTHONANYWHERE_USERNAME}/sira/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Also add the parent directory for imports
parent_dir = f'/home/{PYTHONANYWHERE_USERNAME}/sira'
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================
# Database URL for PythonAnywhere PostgreSQL
os.environ['DATABASE_URL'] = (
    f'postgresql://{PYTHONANYWHERE_USERNAME}:{DATABASE_PASSWORD}'
    f'@{PYTHONANYWHERE_USERNAME}-{DATABASE_NAME}.postgres.pythonanywhere-services.com/{DATABASE_NAME}'
)

# Security settings
os.environ['SECRET_KEY'] = SECRET_KEY
os.environ['DEBUG'] = 'False'
os.environ['LOG_LEVEL'] = 'WARNING'

# CORS settings for production
os.environ['CORS_ORIGINS'] = f'https://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com'

# =============================================================================
# ASGI APPLICATION
# =============================================================================
# PythonAnywhere supports ASGI apps with uvicorn workers
# Make sure you've selected "ASGI" in the web app configuration

from app.main import app

# The 'app' is already an ASGI application (FastAPI)
# PythonAnywhere will use this directly with uvicorn
application = app
