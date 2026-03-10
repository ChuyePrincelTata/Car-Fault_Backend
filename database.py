from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import settings after logging is set up
from config import settings

# Get the appropriate database URL
DATABASE_URL = settings.database_url

# Log the database URL (with password masked)
if "://" in DATABASE_URL:
    parts = DATABASE_URL.split("://")
    if "@" in parts[1]:
        auth_part = parts[1].split("@")[0]
        if ":" in auth_part:
            user = auth_part.split(":")[0]
            masked_url = f"{parts[0]}://{user}:****@{parts[1].split('@')[1]}"
            logger.info(f"Connecting to database: {masked_url}")
    else:
        logger.info(f"Using database: {DATABASE_URL}")
else:
    logger.info(f"Using database: {DATABASE_URL}")

# Create engine with better error handling
try:
    if DATABASE_URL.startswith("sqlite"):
        # SQLite specific configuration
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=settings.debug
        )
        logger.info("Using SQLite database")
    else:
        # PostgreSQL configuration
        engine = create_engine(
            DATABASE_URL,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=300
        )
        logger.info("Using PostgreSQL database")
        
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine created successfully")
    
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    # Fallback to SQLite
    logger.info("Falling back to SQLite database")
    DATABASE_URL = "sqlite:///./carfirstaid_fallback.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.debug
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
