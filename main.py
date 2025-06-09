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
    
    # Create upload directory
    os.makedirs(settings.upload_dir, exist_ok=True)
    logger.info(f"Upload directory created: {settings.upload_dir}")
    
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(mechanics.router, prefix="/api/mechanics", tags=["mechanics"])
app.include_router(diagnostics.router, prefix="/api/diagnostics", tags=["diagnostics"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])

# Add health endpoint directly in main.py
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Car First Aid API",
        "version": "1.0.0"
    }

# Serve uploaded files
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

@app.get("/")
async def root():
    return {
        "message": "Car First Aid API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment
    }

@app.get("/api")
async def api_root():
    return {
        "message": "Car First Aid API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "auth": "/api/auth",
            "users": "/api/users",
            "mechanics": "/api/mechanics",
            "diagnostics": "/api/diagnostics",
            "feedback": "/api/feedback"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
