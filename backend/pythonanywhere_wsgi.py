"""
PythonAnywhere WSGI Configuration for sackson.pythonanywhere.com

Copy this to: /var/www/sackson_pythonanywhere_com_wsgi.py

Then on PythonAnywhere Bash console:
  cd ~/sira/backend
  pip install -r requirements.txt
  pip install a2wsgi
"""

import sys
import os

# Add project to path
project_home = '/home/sackson/sira/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Environment variables — set BEFORE importing the app
os.environ.setdefault('DATABASE_URL', 'postgresql://super:@sackson-5021.postgres.pythonanywhere-services.com:15021/sira')
os.environ.setdefault('SECRET_KEY', 'sira-pythonanywhere-prod-key-change-this-to-something-random-min-32')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('ALLOWED_ORIGINS', 'https://sackson.pythonanywhere.com,http://sackson.pythonanywhere.com')

# Import FastAPI app (WSGI-compatible version without async lifespan)
from app.main_wsgi import app as fastapi_app

# FastAPI is ASGI — PythonAnywhere needs WSGI
# a2wsgi converts ASGI apps to WSGI (pip install a2wsgi)
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(fastapi_app)
