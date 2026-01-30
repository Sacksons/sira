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
venv_path = f'/home/{PYTHONANYWHERE_USERNAME}/.virtualenvs/sira/lib/python3.10/site-packages'

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
# ASGI TO WSGI ADAPTER
# =============================================================================

import asyncio
from io import BytesIO


def asgi_to_wsgi(asgi_app):
    """
    Wrap an ASGI application (FastAPI) to work with WSGI servers (PythonAnywhere).
    This is a synchronous adapter that runs async code in an event loop.
    """
    def wsgi_app(environ, start_response):
        # Build ASGI scope from WSGI environ
        scope = {
            'type': 'http',
            'asgi': {'version': '3.0'},
            'http_version': environ.get('SERVER_PROTOCOL', 'HTTP/1.1').split('/')[-1],
            'method': environ['REQUEST_METHOD'],
            'scheme': environ.get('wsgi.url_scheme', 'http'),
            'path': environ.get('PATH_INFO', '/'),
            'query_string': environ.get('QUERY_STRING', '').encode('utf-8'),
            'root_path': environ.get('SCRIPT_NAME', ''),
            'headers': [],
            'server': (environ.get('SERVER_NAME', 'localhost'),
                      int(environ.get('SERVER_PORT', 80))),
        }

        # Extract headers
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].lower().replace('_', '-')
                scope['headers'].append((header_name.encode(), value.encode()))
            elif key == 'CONTENT_TYPE':
                scope['headers'].append((b'content-type', value.encode()))
            elif key == 'CONTENT_LENGTH':
                scope['headers'].append((b'content-length', value.encode()))

        # Read request body
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError, TypeError):
            content_length = 0

        body = environ['wsgi.input'].read(content_length) if content_length > 0 else b''

        # Response storage
        response_started = False
        response_status = None
        response_headers = []
        response_body = BytesIO()

        async def receive():
            return {'type': 'http.request', 'body': body, 'more_body': False}

        async def send(message):
            nonlocal response_started, response_status, response_headers

            if message['type'] == 'http.response.start':
                response_started = True
                response_status = message['status']
                response_headers = [
                    (name.decode() if isinstance(name, bytes) else name,
                     value.decode() if isinstance(value, bytes) else value)
                    for name, value in message.get('headers', [])
                ]
            elif message['type'] == 'http.response.body':
                body_content = message.get('body', b'')
                if body_content:
                    response_body.write(body_content)

        # Run the ASGI app
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(asgi_app(scope, receive, send))
        finally:
            loop.close()

        # Build WSGI response
        status_phrases = {
            200: 'OK', 201: 'Created', 204: 'No Content',
            301: 'Moved Permanently', 302: 'Found', 304: 'Not Modified',
            400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden',
            404: 'Not Found', 405: 'Method Not Allowed', 422: 'Unprocessable Entity',
            500: 'Internal Server Error', 502: 'Bad Gateway', 503: 'Service Unavailable'
        }
        status_phrase = status_phrases.get(response_status, 'Unknown')
        status_line = f'{response_status} {status_phrase}'

        start_response(status_line, response_headers)
        return [response_body.getvalue()]

    return wsgi_app


# =============================================================================
# WSGI APPLICATION
# =============================================================================

# Import the FastAPI app
from app.main import app as fastapi_app

# Wrap FastAPI (ASGI) for WSGI compatibility
application = asgi_to_wsgi(fastapi_app)
