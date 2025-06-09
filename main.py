from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from contextlib import asynccontextmanager

# Import routers
from routers import auth, users, mechanics, diagnostics, feedback
from database import create_tables
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Car First Aid API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Port: {os.environ.get('PORT', '8000')}")
    
    # Create upload directory
    try:
        os.makedirs(settings.upload_dir, exist_ok=True)
        logger.info(f"Upload directory created: {settings.upload_dir}")
    except Exception as e:
        logger.error(f"Failed to create upload directory: {e}")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue anyway - the app can still work with some limitations
    
    yield
    
    # Shutdown
    logger.info("Shutting down Car First Aid API...")

app = FastAPI(
    title="Car First Aid API",
    description="API for Car First Aid mobile application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - optimized for mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mobile apps need this
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Health endpoints (for mobile app connection testing)
@app.get("/")
async def root():
    return {
        "message": "Car First Aid API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "platform": "mobile-backend"
    }

@app.get("/health")
async def health_check_root():
    """Health check endpoint at root level"""
    return {
        "status": "healthy",
        "service": "Car First Aid API",
        "version": "1.0.0",
        "platform": "mobile-backend"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint for mobile app"""
    return {
        "status": "healthy",
        "service": "Car First Aid API",
        "version": "1.0.0",
        "platform": "mobile-backend"
    }

# Include routers
try:
    app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(mechanics.router, prefix="/api/mechanics", tags=["mechanics"])
    app.include_router(diagnostics.router, prefix="/api/diagnostics", tags=["diagnostics"])
    app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
    logger.info("All routers loaded successfully")
except Exception as e:
    logger.error(f"Failed to load routers: {e}")

@app.get("/api")
async def api_root():
    return {
        "message": "Car First Aid Mobile API",
        "version": "1.0.0",
        "platform": "mobile-backend",
        "endpoints": {
            "health": "/api/health",
            "auth": "/api/auth",
            "users": "/api/users",
            "mechanics": "/api/mechanics",
            "diagnostics": "/api/diagnostics",
            "feedback": "/api/feedback"
        }
    }

# Serve uploaded files
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
