#!/bin/bash
# PythonAnywhere Deployment Script for SIRA Platform
# Run this script on your local machine to deploy to PythonAnywhere

set -e

# Configuration - UPDATE THESE VALUES
PYTHONANYWHERE_USERNAME="${PYTHONANYWHERE_USERNAME:-your_username}"
PYTHONANYWHERE_API_TOKEN="${PYTHONANYWHERE_API_TOKEN:-your_api_token}"
PYTHONANYWHERE_DOMAIN="${PYTHONANYWHERE_DOMAIN:-${PYTHONANYWHERE_USERNAME}.pythonanywhere.com}"
GITHUB_REPO="https://github.com/Sacksons/sira.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SIRA Platform - PythonAnywhere Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if credentials are set
if [ "$PYTHONANYWHERE_USERNAME" == "your_username" ] || [ "$PYTHONANYWHERE_API_TOKEN" == "your_api_token" ]; then
    echo -e "${RED}Error: Please set PYTHONANYWHERE_USERNAME and PYTHONANYWHERE_API_TOKEN${NC}"
    echo "Export them in your shell or update this script"
    echo ""
    echo "  export PYTHONANYWHERE_USERNAME=your_username"
    echo "  export PYTHONANYWHERE_API_TOKEN=your_api_token"
    exit 1
fi

API_BASE="https://www.pythonanywhere.com/api/v0/user/${PYTHONANYWHERE_USERNAME}"

echo -e "\n${YELLOW}Step 1: Testing API connection...${NC}"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    "${API_BASE}/cpu/" \
    -H "Authorization: Token ${PYTHONANYWHERE_API_TOKEN}")

if [ "$RESPONSE" != "200" ]; then
    echo -e "${RED}Error: API connection failed (HTTP $RESPONSE)${NC}"
    echo "Please check your API token"
    exit 1
fi
echo -e "${GREEN}API connection successful!${NC}"

echo -e "\n${YELLOW}Step 2: Creating/updating console to pull latest code...${NC}"
# Create a bash console command to pull code
CONSOLE_COMMAND="cd ~/sira && git pull origin main 2>&1 || (cd ~ && git clone ${GITHUB_REPO} sira 2>&1)"

# Start a console
CONSOLE_RESPONSE=$(curl -s -X POST \
    "${API_BASE}/consoles/" \
    -H "Authorization: Token ${PYTHONANYWHERE_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"executable": "bash", "arguments": "", "working_directory": "/home/'"${PYTHONANYWHERE_USERNAME}"'"}')

CONSOLE_ID=$(echo $CONSOLE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null || echo "")

if [ -z "$CONSOLE_ID" ]; then
    echo -e "${YELLOW}Note: Could not create console via API. You may need to run commands manually.${NC}"
else
    echo -e "${GREEN}Console created: $CONSOLE_ID${NC}"
fi

echo -e "\n${YELLOW}Step 3: Reloading web app...${NC}"
RELOAD_RESPONSE=$(curl -s -X POST \
    "${API_BASE}/webapps/${PYTHONANYWHERE_DOMAIN}/reload/" \
    -H "Authorization: Token ${PYTHONANYWHERE_API_TOKEN}")

echo -e "${GREEN}Web app reload triggered!${NC}"

echo -e "\n${YELLOW}Step 4: Checking web app status...${NC}"
sleep 3
STATUS_RESPONSE=$(curl -s \
    "${API_BASE}/webapps/${PYTHONANYWHERE_DOMAIN}/" \
    -H "Authorization: Token ${PYTHONANYWHERE_API_TOKEN}")

echo "$STATUS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"  Domain: {data.get('domain_name', 'N/A')}\")
print(f\"  Python: {data.get('python_version', 'N/A')}\")
print(f\"  Source: {data.get('source_directory', 'N/A')}\")
" 2>/dev/null || echo "Could not parse status"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nYour app should be available at:"
echo -e "  ${GREEN}https://${PYTHONANYWHERE_DOMAIN}${NC}"
echo ""
echo "If this is your first deployment, you need to:"
echo "1. Log into PythonAnywhere"
echo "2. Open a Bash console"
echo "3. Run these commands:"
echo ""
echo "   cd ~"
echo "   git clone ${GITHUB_REPO} sira"
echo "   cd sira/backend"
echo "   mkvirtualenv --python=/usr/bin/python3.11 sira"
echo "   pip install -r requirements.txt"
echo "   cp .env.example .env"
echo "   # Edit .env with your settings"
echo "   alembic upgrade head"
echo "   python create_admin.py"
echo ""
echo "4. Configure the web app in PythonAnywhere Dashboard:"
echo "   - Source code: /home/${PYTHONANYWHERE_USERNAME}/sira/backend"
echo "   - Working directory: /home/${PYTHONANYWHERE_USERNAME}/sira/backend"
echo "   - Virtualenv: /home/${PYTHONANYWHERE_USERNAME}/.virtualenvs/sira"
echo "   - WSGI file: Use the content from backend/pythonanywhere_wsgi.py"
