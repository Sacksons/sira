"""
SIRA Platform - Main Application Entry Point
Shipping Intelligence & Risk Analytics Platform

Serves both the API (/api/*) and the frontend SPA (all other routes).
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import logging
import time

from app.core.config import settings
from app.core.database import init_db, engine, Base
from app.api import api_router

# Frontend dist directory (copied into Docker container at /app/frontend/dist/)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _ensure_admin_user():
    """Create admin user if it doesn't exist (runs on every startup for cloud deploys)"""
    from app.core.database import SessionLocal
    from app.core.security import hash_password
    from app.models.user import User

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            admin = User(
                username="admin",
                email="admin@sira.com",
                full_name="SIRA Administrator",
                hashed_password=hash_password("admin123"),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Admin user created (admin / admin123)")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error ensuring admin user: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting SIRA Platform API...")
    try:
        init_db()
        _ensure_admin_user()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed (app will start anyway): {e}")
    logger.info(f"SIRA Platform API v{settings.APP_VERSION} started successfully")

    yield

    # Shutdown
    logger.info("Shutting down SIRA Platform API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## SIRA Platform API

    **Shipping Intelligence & Risk Analytics Platform**
    **Multimodal Control Tower + Fleet Management + Market Intelligence + AI**

    Sponsored by: Energie Partners (EP)

    ### Core Modules:
    - **Multimodal Control Tower**: Real-time operational visibility across all assets and corridor segments
    - **Vessel Tracking**: AIS-integrated vessel position tracking and charter management
    - **Fleet & Asset Management**: Truck, rail, barge, and equipment lifecycle management with dispatch
    - **Port & Terminal Operations**: Berth allocation, anchorage management, and congestion tracking
    - **Shipment Workspace**: End-to-end shipment tracking with milestones and exception management
    - **Market Intelligence**: Freight rate benchmarks, market indices, and demurrage analytics
    - **Chain-of-Custody**: Digital seals, audit trails, and tamper-evident custody tracking
    - **SIRA AI**: ETA prediction, demurrage risk scoring, and anomaly detection

    ### Legacy Modules:
    - **Security Intelligence**: Monitor events, manage alerts, and investigate incidents
    - **Case Management**: Handle security cases with evidence tracking
    - **Playbook System**: Standardized incident response procedures
    - **Real-time Notifications**: WebSocket and email alerts

    ### Authentication:
    All endpoints (except `/health` and `/api/v1/auth/token`) require authentication.
    Use the `/api/v1/auth/token` endpoint to obtain an access token.
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware - allow all origins for cross-domain API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Request timing middleware - also adds CORS headers as fallback
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start_time = time.time()

    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        response = JSONResponse(content={}, status_code=200)
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
        return response

    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    # Ensure CORS headers are always present
    origin = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint — must respond fast for Railway healthcheck
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    from datetime import datetime, timezone

    result = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Try DB check but don't block if it's slow/unavailable
    try:
        from app.core.database import check_db_connection
        db_ok = check_db_connection()
        result["database"] = "healthy" if db_ok else "unhealthy"
        if not db_ok:
            result["status"] = "degraded"
    except Exception as e:
        result["database"] = f"error: {e}"
        result["status"] = "degraded"

    return result


# Test login endpoint (debug - remove after fixing)
@app.get("/test-login", tags=["Debug"])
async def test_login():
    """Test that login works - tries admin/admin123 directly"""
    from app.core.database import SessionLocal
    from app.core.security import verify_password, create_access_token
    from app.models.user import User

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            return {"status": "FAIL", "reason": "admin user not found in database"}

        password_ok = verify_password("admin123", user.hashed_password)
        if not password_ok:
            return {"status": "FAIL", "reason": "password verification failed", "hash_prefix": user.hashed_password[:20]}

        token = create_access_token(
            data={"sub": user.username, "role": user.role, "user_id": user.id}
        )
        return {
            "status": "OK",
            "message": "Login works! admin/admin123 is valid",
            "token_preview": token[:30] + "...",
            "user_id": user.id,
            "role": user.role,
            "is_active": user.is_active,
        }
    finally:
        db.close()


# Include API router (must be before SPA catch-all)
app.include_router(api_router, prefix="/api")

# --- Frontend SPA serving ---
# Mount frontend static assets (JS/CSS bundles)
if FRONTEND_DIR.exists() and (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="static-assets")
    logger.info(f"Serving frontend assets from {FRONTEND_DIR / 'assets'}")


# SPA catch-all: serve index.html for all non-API routes
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(request: Request, full_path: str):
    """Serve the React SPA for all non-API routes"""
    # If frontend is built, serve index.html
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    # Fallback: API info (no frontend built)
    return JSONResponse({
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Shipping Intelligence & Risk Analytics Platform",
        "docs": "/docs",
        "health": "/health",
    })


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
