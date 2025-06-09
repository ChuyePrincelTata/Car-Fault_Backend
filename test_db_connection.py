#!/usr/bin/env python3
"""
Test script to verify database connectivity
"""
import sys
import logging
from sqlalchemy import create_engine, text
from config import settings, get_database_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and create tables if needed"""
    database_url = get_database_url()
    logger.info(f"Testing connection to: {database_url}")
    
    try:
        # Create engine
        if database_url.startswith("sqlite"):
            engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False}
            )
        else:
            engine = create_engine(database_url, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful!")
            
        # Test table creation
        from database import Base, create_tables
        create_tables()
        logger.info("✅ Database tables created/verified successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
