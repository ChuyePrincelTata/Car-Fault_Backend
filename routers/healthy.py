from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import time

router = APIRouter()

@router.get("")
async def health_check():
    """
    Simple health check endpoint that returns status 200 OK.
    This is used by the mobile app to test connectivity.
    """
    return {"status": "healthy", "timestamp": time.time()}

@router.get("/db")
async def db_health_check(db: Session = Depends(get_db)):
    """
    Database health check endpoint.
    Tests if the database connection is working.
    """
    try:
        # Simple query to test database connection
        db.execute("SELECT 1").first()
        return {"status": "healthy", "database": "connected", "timestamp": time.time()}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e), "timestamp": time.time()}
