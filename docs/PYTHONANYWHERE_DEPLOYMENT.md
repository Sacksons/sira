# PythonAnywhere Deployment Guide for SIRA

This guide walks you through deploying the SIRA platform to PythonAnywhere.

## Prerequisites

- PythonAnywhere account (Hacker plan or above recommended for custom domains)
- GitHub repository with SIRA code pushed

## Quick Start Checklist

- [ ] Create PythonAnywhere account
- [ ] Clone repository
- [ ] Set up virtual environment
- [ ] Create and configure MySQL database
- [ ] Configure environment variables
- [ ] Set up WSGI file
- [ ] Configure static files
- [ ] Test deployment

## Step 1: Create PythonAnywhere Account

1. Go to [PythonAnywhere](https://www.pythonanywhere.com)
2. Sign up for an account (Hacker plan recommended)
3. Verify your email

## Step 2: Clone Repository

1. Open a **Bash console** from the Dashboard
2. Clone your repository:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/sira.git
cd sira
```

## Step 3: Set Up Virtual Environment

```bash
# Create virtual environment with Python 3.11
mkvirtualenv --python=/usr/bin/python3.11 sira

# Activate it (if not already active)
workon sira

# Install backend dependencies (use PythonAnywhere-specific requirements)
cd ~/sira/backend
pip install -r requirements-pythonanywhere.txt
```

**Note:** We use `requirements-pythonanywhere.txt` which includes MySQL support and excludes development dependencies.

## Step 4: Configure Environment Variables

1. Create the `.env` file:

```bash
cd ~/sira/backend
cp .env.example .env
nano .env
```

2. Update the following values:

```env
# Database - Use MySQL on PythonAnywhere
DATABASE_URL=mysql+pymysql://YOUR_USERNAME$sira:YOUR_DB_PASSWORD@YOUR_USERNAME.mysql.pythonanywhere-services.com/YOUR_USERNAME$sira

# Security - Generate new keys!
SECRET_KEY=your-super-secret-key-generate-with-openssl-rand-hex-32
JWT_SECRET_KEY=your-jwt-secret-key-generate-with-openssl-rand-hex-32

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Environment
ENVIRONMENT=production
DEBUG=false
```

Generate secure keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 5: Set Up MySQL Database

1. Go to **Databases** tab on PythonAnywhere Dashboard
2. Set a MySQL password
3. Create a database named `YOUR_USERNAME$sira`
4. Note down the database host: `YOUR_USERNAME.mysql.pythonanywhere-services.com`

## Step 6: Initialize Database

```bash
workon sira
cd ~/sira/backend

# Run migrations
alembic upgrade head

# Create admin user
python create_admin.py
```

## Step 7: Configure Web App

1. Go to **Web** tab on PythonAnywhere Dashboard
2. Click **Add a new web app**
3. Select **Manual configuration**
4. Choose **Python 3.11**

### Configure Virtual Environment

In the **Virtualenv** section:
```
/home/YOUR_USERNAME/.virtualenvs/sira
```

### Configure WSGI File

1. Click on the WSGI configuration file link (e.g., `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`)
2. Delete all contents and copy the content from `backend/pythonanywhere_wsgi.py`
3. **Important:** Replace all placeholders with your actual values:
   - Replace `<username>` with your PythonAnywhere username
   - Replace `<db_password>` with your MySQL password
   - Generate and set unique `SECRET_KEY` and `JWT_SECRET_KEY` values

```python
import sys
import os

# Replace with your PythonAnywhere username
PYTHONANYWHERE_USERNAME = 'YOUR_USERNAME'

# Project paths
project_home = f'/home/{PYTHONANYWHERE_USERNAME}/sira/backend'
venv_path = f'/home/{PYTHONANYWHERE_USERNAME}/.virtualenvs/sira/lib/python3.11/site-packages'

if project_home not in sys.path:
    sys.path.insert(0, project_home)
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Set environment variables
os.environ['DATABASE_URL'] = f'mysql+pymysql://{PYTHONANYWHERE_USERNAME}$sira:YOUR_PASSWORD@{PYTHONANYWHERE_USERNAME}.mysql.pythonanywhere-services.com/{PYTHONANYWHERE_USERNAME}$sira'
os.environ['SECRET_KEY'] = 'your-generated-secret-key'
os.environ['JWT_SECRET_KEY'] = 'your-generated-jwt-secret-key'
os.environ['ENVIRONMENT'] = 'production'
os.environ['DEBUG'] = 'False'
os.environ['LOG_LEVEL'] = 'WARNING'
os.environ['CORS_ORIGINS'] = f'https://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com'

# Import the FastAPI app and wrap it for WSGI
from app.main import app as fastapi_app
from asgi_wsgi_translator import asgi_to_wsgi
application = asgi_to_wsgi(fastapi_app)
```

**Generate secure keys:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 8: Configure Static Files (Frontend)

### Build Frontend Locally

On your local machine:
```bash
cd frontend
npm install
npm run build
```

### Upload to PythonAnywhere

1. Upload the `dist` folder contents to `/home/YOUR_USERNAME/sira/frontend/dist`
2. In the **Web** tab, add a static file mapping:

| URL | Directory |
|-----|-----------|
| /static | /home/YOUR_USERNAME/sira/frontend/dist |
| /assets | /home/YOUR_USERNAME/sira/frontend/dist/assets |

## Step 9: Configure CORS

Update `backend/app/main.py` with your PythonAnywhere domain:

```python
origins = [
    "https://YOUR_USERNAME.pythonanywhere.com",
    "http://YOUR_USERNAME.pythonanywhere.com",
]
```

## Step 10: Reload Web App

1. Go to **Web** tab
2. Click **Reload** button

## Step 11: Verify Deployment

1. Visit `https://YOUR_USERNAME.pythonanywhere.com/health`
2. You should see: `{"status": "healthy", "version": "1.0.0"}`

## Step 12: Access the Application

- API Docs: `https://YOUR_USERNAME.pythonanywhere.com/docs`
- Frontend: `https://YOUR_USERNAME.pythonanywhere.com`

## Troubleshooting

### View Error Logs

```bash
# In PythonAnywhere console
cat /var/log/YOUR_USERNAME.pythonanywhere.com.error.log
```

### Common Issues

1. **ModuleNotFoundError**: Ensure virtualenv is correctly configured
2. **Database connection errors**: Verify MySQL credentials and host
3. **Static files not loading**: Check static file mappings

### Updating the Application

```bash
cd ~/sira
git pull origin main
workon sira
cd backend
pip install -r requirements.txt
alembic upgrade head
```

Then reload the web app from the Dashboard.

## Custom Domain (Optional)

1. Go to **Web** tab
2. Add your custom domain
3. Configure DNS CNAME record pointing to `webapp-XXXXXX.pythonanywhere.com`

## Scheduled Tasks

For background tasks (optional):

1. Go to **Tasks** tab
2. Add daily task:
```bash
workon sira && cd ~/sira/backend && python -c "from app.services.alert_engine import AlertEngine; AlertEngine().process_pending_events()"
```

## CI/CD Auto-Deployment (Optional)

To enable automatic deployments when you push to the main branch:

### 1. Get PythonAnywhere API Token

1. Go to **Account** > **API Token** on PythonAnywhere
2. Generate a new API token
3. Copy and save the token securely

### 2. Configure GitHub Secrets

Go to your GitHub repository **Settings** > **Secrets and variables** > **Actions**, and add:

| Secret Name | Value |
|-------------|-------|
| `PYTHONANYWHERE_USERNAME` | Your PythonAnywhere username |
| `PYTHONANYWHERE_API_TOKEN` | Your API token from step 1 |
| `DATABASE_URL` | Your PythonAnywhere MySQL connection string |

### 3. Run Deployment

1. Go to **Actions** tab in GitHub
2. Select **Deploy SIRA Platform** workflow
3. Click **Run workflow**
4. Select `production` environment
5. Click **Run workflow**

The workflow will pull the latest code and reload your web app automatically.

## Security Checklist

- [ ] Changed default SECRET_KEY (generate with `secrets.token_hex(32)`)
- [ ] Changed default JWT_SECRET_KEY (generate with `secrets.token_hex(32)`)
- [ ] Set DEBUG=False in WSGI file
- [ ] HTTPS enabled (automatic on *.pythonanywhere.com)
- [ ] Set strong MySQL database password
- [ ] Created unique admin password (run `python create_admin.py`)
- [ ] Verified CORS_ORIGINS only includes your domain
- [ ] Removed or secured any test/demo endpoints
