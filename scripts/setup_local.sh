#!/bin/bash
# SIRA Platform - Local Development Setup Script

set -e

echo "=========================================="
echo "SIRA Platform - Local Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python3 --version

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Backend setup
echo -e "\n${YELLOW}Setting up backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}Please update .env with your configuration${NC}"
fi

# Create uploads directory
mkdir -p uploads

echo -e "${GREEN}Backend setup complete!${NC}"

# Frontend setup
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd "$PROJECT_ROOT/frontend"

# Check if npm is installed
if command -v npm &> /dev/null; then
    echo "Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}Frontend setup complete!${NC}"
else
    echo -e "${YELLOW}npm not found. Please install Node.js to set up the frontend.${NC}"
fi

# Return to project root
cd "$PROJECT_ROOT"

echo -e "\n=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "To start the frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
echo ""
