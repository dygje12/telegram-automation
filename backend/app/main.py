from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database
from app.database import connect_db, disconnect_db, engine, Base

# Import services
from app.services.scheduler_service import scheduler_service

# Import routers
from app.routers import auth, messages, groups, blacklist, scheduler, settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Telegram Automation API...")
    
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
    
    yield
    
    # Shutdown
    logger.info("Shutting down Telegram Automation API...")
    
    # Stop scheduler
    scheduler_service.stop_scheduler()
    logger.info("Scheduler stopped")
    
    # Disconnect from database
    await disconnect_db()
    logger.info("Database disconnected")

# Create FastAPI app
app = FastAPI(
    title="Telegram Automation API",
    description="API for automating Telegram message sending using user accounts",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(groups.router)
app.include_router(blacklist.router)
app.include_router(scheduler.router)
app.include_router(settings.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "success": False,
            "error_code": "INTERNAL_ERROR"
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from app.database import database
        
        # Check scheduler status
        scheduler_running = scheduler_service.scheduler.running if scheduler_service.scheduler else False
        
        return {
            "status": "healthy",
            "database": "connected",
            "scheduler": "running" if scheduler_running else "stopped",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Telegram Automation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/auth",
            "messages": "/messages",
            "groups": "/groups",
            "blacklist": "/blacklist",
            "scheduler": "/scheduler",
            "settings": "/settings"
        }
    }

# API info endpoint
@app.get("/info")
async def api_info():
    """Get API information and statistics"""
    try:
        # Get basic stats
        stats = {
            "api_version": "1.0.0",
            "scheduler_running": scheduler_service.scheduler.running if scheduler_service.scheduler else False,
            "active_jobs": len(scheduler_service.running_jobs),
            "features": [
                "Telegram user account authentication",
                "Message template management",
                "Group management with validation",
                "Smart blacklist management",
                "Automated message scheduling",
                "Real-time monitoring and logging",
                "Configurable sending intervals"
            ]
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get API info: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

