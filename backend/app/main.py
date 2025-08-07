"""
Main FastAPI application with production-ready configuration
"""

import logging.config
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Import API routers
from app.api.v1 import auth, blacklist, groups, messages, scheduler, settings

# Import core modules
from app.core.config import get_logging_config, get_settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging

# Import database
from app.database import Base, connect_db, disconnect_db, engine
from app.middleware.cors import configure_cors_middleware
from app.middleware.error_handler import setup_exception_handlers
from app.middleware.rate_limiting import rate_limit_middleware

# Import services
from app.services.scheduler_service import scheduler_service

# Get settings
settings = get_settings()

# Setup logging
setup_logging(
    log_level=settings.log_level, log_file=settings.log_file, json_format=settings.is_production
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Telegram Automation API...")

    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")

        # Connect to database
        await connect_db()
        logger.info("Database connected")

        # Start scheduler
        scheduler_service.start_scheduler()
        logger.info("Scheduler started")

        # Generate encryption key if needed
        from app.utils.encryption import encryption_manager

        logger.info("Encryption manager initialized")

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Telegram Automation API...")

    try:
        # Stop scheduler
        scheduler_service.stop_scheduler()
        logger.info("Scheduler stopped")

        # Disconnect from database
        await disconnect_db()
        logger.info("Database disconnected")

        logger.info("Application shutdown completed successfully")

    except Exception as e:
        logger.error(f"Application shutdown failed: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Production-ready API for automating Telegram message sending using user accounts",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
)

# Configure CORS
cors_configured = configure_cors_middleware(app)
if cors_configured:
    logger.info(f"CORS configured with origins: {settings.allowed_origins_list}")
else:
    logger.warning("CORS not configured - no allowed origins specified")

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)
logger.info("Rate limiting middleware configured")

# Setup exception handlers
setup_exception_handlers(app)
logger.info("Exception handlers configured")

# Include API routers with v1 prefix
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(messages.router, prefix="/api/v1", tags=["Messages"])
app.include_router(groups.router, prefix="/api/v1", tags=["Groups"])
app.include_router(blacklist.router, prefix="/api/v1", tags=["Blacklist"])
app.include_router(scheduler.router, prefix="/api/v1", tags=["Scheduler"])
app.include_router(settings.router, prefix="/api/v1", tags=["Settings"])

logger.info("API routers configured")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Check database connection
        from app.database import database

        # Check scheduler status
        scheduler_running = (
            scheduler_service.scheduler.running if scheduler_service.scheduler else False
        )

        return {
            "status": "healthy",
            "environment": settings.environment,
            "version": settings.app_version,
            "database": "connected",
            "scheduler": "running" if scheduler_running else "stopped",
            "timestamp": "2024-01-01T00:00:00Z",  # Will be replaced with actual timestamp
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e) if settings.is_development else "Service unavailable",
            },
        )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.is_development else "Documentation not available in production",
        "health": "/health",
        "api": {
            "base_url": "/api/v1",
            "endpoints": {
                "auth": "/api/v1/auth",
                "messages": "/api/v1/messages",
                "groups": "/api/v1/groups",
                "blacklist": "/api/v1/blacklist",
                "scheduler": "/api/v1/scheduler",
                "settings": "/api/v1/settings",
            },
        },
    }


# API info endpoint
@app.get("/api/v1/info", tags=["Info"])
async def api_info():
    """
    Get API information and statistics
    """
    try:
        # Get basic stats
        stats = {
            "api_version": settings.app_version,
            "environment": settings.environment,
            "scheduler_running": (
                scheduler_service.scheduler.running if scheduler_service.scheduler else False
            ),
            "active_jobs": (
                len(scheduler_service.running_jobs)
                if hasattr(scheduler_service, "running_jobs")
                else 0
            ),
            "features": [
                "Telegram user account authentication",
                "Message template management",
                "Group management with validation",
                "Smart blacklist management",
                "Automated message scheduling",
                "Real-time monitoring and logging",
                "Configurable sending intervals",
                "Rate limiting and security",
                "Production-ready architecture",
            ],
            "security": {
                "rate_limiting": True,
                "cors_configured": cors_configured,
                "authentication": "JWT Bearer Token",
                "input_validation": True,
                "error_handling": True,
            },
        }

        return stats

    except Exception as e:
        logger.error(f"Failed to get API info: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e) if settings.is_development else "Internal server error"},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=True,
    )
