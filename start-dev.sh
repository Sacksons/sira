#!/bin/bash
# SIRA Platform - Local Development Startup Script
# Usage: ./start-dev.sh [backend|frontend|setup|all]

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[SIRA]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

setup_backend() {
    log "Setting up backend..."
    cd "$BACKEND_DIR"

    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
    fi

    source venv/bin/activate
    log "Installing Python dependencies..."
    pip install -r requirements.txt -q 2>/dev/null || pip install -r requirements.txt

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log "Created .env from .env.example"
        fi
    fi

    log "Setting up database and seed data..."
    python setup_dev.py

    log "Backend setup complete!"
}

setup_frontend() {
    log "Setting up frontend..."
    cd "$FRONTEND_DIR"

    if [ ! -d "node_modules" ]; then
        log "Installing npm dependencies..."
        npm install
    fi

    log "Frontend setup complete!"
}

start_backend() {
    cd "$BACKEND_DIR"
    if [ ! -d "venv" ]; then
        error "Backend not set up. Run: ./start-dev.sh setup"
        exit 1
    fi
    source venv/bin/activate
    log "Starting FastAPI backend on ${BLUE}http://localhost:8000${NC}"
    log "API docs available at ${BLUE}http://localhost:8000/docs${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

start_frontend() {
    cd "$FRONTEND_DIR"
    if [ ! -d "node_modules" ]; then
        error "Frontend not set up. Run: ./start-dev.sh setup"
        exit 1
    fi
    log "Starting Vite dev server on ${BLUE}http://localhost:3000${NC}"
    npm run dev
}

start_all() {
    log "Starting SIRA Platform (Full Stack)..."
    log "=================================="

    # Start backend in background
    cd "$BACKEND_DIR"
    source venv/bin/activate
    log "Starting backend on port 8000..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!

    # Wait for backend to be ready
    sleep 3

    # Start frontend in foreground
    cd "$FRONTEND_DIR"
    log "Starting frontend on port 3000..."
    log ""
    log "=================================="
    log "SIRA Platform is running!"
    log "  Frontend: ${BLUE}http://localhost:3000${NC}"
    log "  Backend:  ${BLUE}http://localhost:8000${NC}"
    log "  API Docs: ${BLUE}http://localhost:8000/docs${NC}"
    log "  Login:    admin / admin123"
    log "=================================="
    log ""

    # Trap to kill backend when script exits
    trap "kill $BACKEND_PID 2>/dev/null" EXIT

    npm run dev
}

case "${1:-all}" in
    setup)
        setup_backend
        setup_frontend
        log ""
        log "Setup complete! Run ./start-dev.sh to start the platform."
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all)
        start_all
        ;;
    *)
        echo "Usage: ./start-dev.sh [setup|backend|frontend|all]"
        echo ""
        echo "  setup     - Install dependencies and seed database"
        echo "  backend   - Start FastAPI backend only (port 8000)"
        echo "  frontend  - Start Vite frontend only (port 3000)"
        echo "  all       - Start both backend and frontend (default)"
        ;;
esac
