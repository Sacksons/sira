"""
PythonAnywhere WSGI Configuration for SIRA Platform

SETUP INSTRUCTIONS:
1. Copy this file content to /var/www/<username>_pythonanywhere_com_wsgi.py
2. Replace all placeholders (<username>, <password>, etc.) with your actual values
3. Make sure you have created and configured your MySQL database on PythonAnywhere
4. Ensure the virtual environment is set up correctly in the Web tab

For detailed instructions, see: docs/PYTHONANYWHERE_DEPLOYMENT.md
"""

import sys
import os

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

# Replace <username> with your PythonAnywhere username
PYTHONANYWHERE_USERNAME = '<username>'

# Project paths
project_home = f'/home/{PYTHONANYWHERE_USERNAME}/sira/backend'
venv_path = f'/home/{PYTHONANYWHERE_USERNAME}/.virtualenvs/sira/lib/python3.11/site-packages'

# Add paths to sys.path
if project_home not in sys.path:
    sys.path.insert(0, project_home)
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

# Database Configuration (MySQL on PythonAnywhere)
# Format: mysql+pymysql://<username>$<dbname>:<password>@<username>.mysql.pythonanywhere-services.com/<username>$<dbname>
os.environ['DATABASE_URL'] = f'mysql+pymysql://{PYTHONANYWHERE_USERNAME}$sira:<db_password>@{PYTHONANYWHERE_USERNAME}.mysql.pythonanywhere-services.com/{PYTHONANYWHERE_USERNAME}$sira'

# Security Keys - IMPORTANT: Generate unique keys for production!
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
os.environ['SECRET_KEY'] = 'your-production-secret-key-change-this'
os.environ['JWT_SECRET_KEY'] = 'your-production-jwt-secret-key-change-this'

# Application Settings
os.environ['ENVIRONMENT'] = 'production'
os.environ['DEBUG'] = 'False'
os.environ['LOG_LEVEL'] = 'WARNING'

# CORS Configuration
os.environ['CORS_ORIGINS'] = f'https://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com,http://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com'

# Optional: Email Configuration (uncomment and configure if needed)
# os.environ['SMTP_HOST'] = 'smtp.gmail.com'
# os.environ['SMTP_PORT'] = '587'
# os.environ['SMTP_USER'] = 'your-email@gmail.com'
# os.environ['SMTP_PASSWORD'] = 'your-app-password'

# =============================================================================
# WSGI APPLICATION
# =============================================================================

# Import the FastAPI app
from app.main import app as fastapi_app

# PythonAnywhere uses WSGI, but FastAPI is ASGI
# We use asgi-wsgi-translator to bridge the gap
try:
    from asgi_wsgi_translator import asgi_to_wsgi
    application = asgi_to_wsgi(fastapi_app)
except ImportError:
    # Fallback: Try using the app directly (may have limited functionality)
    # This works for basic requests but async features won't work properly
    import warnings
    warnings.warn(
        "asgi-wsgi-translator not installed. Install with: pip install a]sgi-wsgi-translator. "
        "Running in fallback mode with limited async support."
    )
    application = fastapi_app
