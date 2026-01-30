# SIRA Platform - PythonAnywhere Deployment Guide

This guide covers deploying the SIRA platform to PythonAnywhere from GitHub.

## Prerequisites

1. A PythonAnywhere account (free tier works for testing)
2. Your code pushed to GitHub at `https://github.com/Sacksons/sira.git`
3. PythonAnywhere API token (get from Account > API Token)

## Initial Setup (First-Time Deployment)

### 1. Create PostgreSQL Database

1. Log into PythonAnywhere
2. Go to **Databases** tab
3. Create a new PostgreSQL database
4. Note your database name and password

### 2. Clone Repository

Open a **Bash console** on PythonAnywhere and run:

```bash
cd ~
git clone https://github.com/Sacksons/sira.git sira
cd sira/backend
```

### 3. Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.11 sira
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cd ~/sira/backend
cp .env.example .env
nano .env
```

Update the `.env` file with your production settings:

```
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_DB_PASSWORD@YOUR_USERNAME-sira.postgres.pythonanywhere-services.com/sira
SECRET_KEY=your-strong-random-secret-key-here
DEBUG=False
LOG_LEVEL=WARNING
```

### 5. Initialize Database

```bash
cd ~/sira/backend
workon sira
alembic upgrade head
python create_admin.py
```

### 6. Configure Web App

1. Go to **Web** tab on PythonAnywhere
2. Click **Add a new web app**
3. Choose **Manual configuration** (not Flask/Django)
4. Select **Python 3.11**
5. Configure these settings:

| Setting | Value |
|---------|-------|
| Source code | `/home/YOUR_USERNAME/sira/backend` |
| Working directory | `/home/YOUR_USERNAME/sira/backend` |
| Virtualenv | `/home/YOUR_USERNAME/.virtualenvs/sira` |

### 7. Configure WSGI

1. Click on the WSGI configuration file link
2. Replace the contents with:

```python
import sys
import os

PYTHONANYWHERE_USERNAME = 'YOUR_USERNAME'
DATABASE_NAME = 'sira'
DATABASE_PASSWORD = 'YOUR_DB_PASSWORD'
SECRET_KEY = 'your-strong-random-secret-key-here'

project_home = f'/home/{PYTHONANYWHERE_USERNAME}/sira/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DATABASE_URL'] = (
    f'postgresql://{PYTHONANYWHERE_USERNAME}:{DATABASE_PASSWORD}'
    f'@{PYTHONANYWHERE_USERNAME}-{DATABASE_NAME}.postgres.pythonanywhere-services.com/{DATABASE_NAME}'
)
os.environ['SECRET_KEY'] = SECRET_KEY
os.environ['DEBUG'] = 'False'
os.environ['LOG_LEVEL'] = 'WARNING'
os.environ['CORS_ORIGINS'] = f'https://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com'

from app.main import app
application = app
```

### 8. Reload Web App

Click the **Reload** button on the Web tab.

Your app should now be available at: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Automated Deployment (CI/CD)

Once the initial setup is complete, deployments happen automatically when you push to `main`.

### GitHub Secrets Setup

Add these secrets to your GitHub repository (Settings > Secrets > Actions):

| Secret | Value |
|--------|-------|
| `PYTHONANYWHERE_USERNAME` | Your PythonAnywhere username |
| `PYTHONANYWHERE_API_TOKEN` | Your API token from PythonAnywhere |

### Manual Deployment

To trigger a deployment manually, run locally:

```bash
export PYTHONANYWHERE_USERNAME=your_username
export PYTHONANYWHERE_API_TOKEN=your_api_token
./scripts/deploy_pythonanywhere.sh
```

---

## Updating the Deployment

### Pull Latest Code (Manual)

```bash
cd ~/sira
git pull origin main
cd backend
workon sira
pip install -r requirements.txt
alembic upgrade head
```

Then reload the web app from the PythonAnywhere dashboard.

### View Logs

Error logs are available at:
- `/var/log/YOUR_USERNAME.pythonanywhere.com.error.log`
- `/var/log/YOUR_USERNAME.pythonanywhere.com.server.log`

---

## Troubleshooting

### Common Issues

1. **500 Internal Server Error**
   - Check the error log for details
   - Verify DATABASE_URL is correct
   - Ensure all migrations have run

2. **Static Files Not Loading**
   - Configure static file mappings in PythonAnywhere Web tab
   - URL: `/static/` → Directory: `/home/YOUR_USERNAME/sira/backend/static`

3. **Database Connection Error**
   - Verify PostgreSQL is running (Databases tab)
   - Check credentials in WSGI file
   - Ensure you're using the correct hostname format

4. **Import Errors**
   - Verify virtualenv path is correct
   - Check that all dependencies are installed
   - Ensure Python version matches (3.11)

### Checking App Status

```bash
curl -s "https://www.pythonanywhere.com/api/v0/user/YOUR_USERNAME/webapps/YOUR_USERNAME.pythonanywhere.com/" \
  -H "Authorization: Token YOUR_API_TOKEN" | python3 -m json.tool
```

---

## Frontend Deployment

For the React frontend, you have two options:

### Option 1: Build and Serve from PythonAnywhere

```bash
cd ~/sira/frontend
npm install
npm run build
# Copy dist/ contents to a static directory
```

### Option 2: Deploy to a CDN (Recommended)

Deploy the frontend to Vercel, Netlify, or similar:

1. Connect your GitHub repo
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Set environment variable: `VITE_API_URL=https://YOUR_USERNAME.pythonanywhere.com`
