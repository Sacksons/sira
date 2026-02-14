"""
SIRA Platform - Main Application Entry Point
Shipping Intelligence & Risk Analytics Platform
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.database import init_db, engine, Base
from app.api import api_router

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
    init_db()
    _ensure_admin_user()
    logger.info("Database initialized")
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

# CORS middleware - handle wildcard properly
cors_origins = settings.cors_origins
if "*" in cors_origins:
    # Wildcard with credentials doesn't work, allow all origins without credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    from datetime import datetime, timezone
    from app.core.database import check_db_connection, SessionLocal
    from app.models.user import User

    db_status = "healthy" if check_db_connection() else "unhealthy"

    # Check if admin user exists
    admin_exists = False
    user_count = 0
    db_url_prefix = settings.DATABASE_URL[:30] if settings.DATABASE_URL else "NOT SET"
    try:
        db = SessionLocal()
        admin = db.query(User).filter(User.username == "admin").first()
        admin_exists = admin is not None
        user_count = db.query(User).count()
        db.close()
    except Exception as e:
        db_url_prefix = f"ERROR: {e}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.APP_VERSION,
        "database": db_status,
        "database_url": db_url_prefix + "...",
        "admin_user_exists": admin_exists,
        "total_users": user_count,
        "cors_origins": settings.cors_origins,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Shipping Intelligence & Risk Analytics Platform",
        "docs": "/docs",
        "health": "/health"
    }


# Include API router
app.include_router(api_router, prefix="/api")


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
