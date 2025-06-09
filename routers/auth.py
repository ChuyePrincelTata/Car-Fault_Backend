from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DatabaseError
from database import get_db
from models import User, Mechanic
from schemas import UserCreate, UserLogin, Token, User as UserSchema
from auth import verify_password, get_password_hash, create_access_token
from config import settings
import time
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=Token)
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    start_time = time.time()
    logger.info(f"Registration request received for email: {user_data.email}")
    
    try:
        # Check if user already exists - optimize query
        db_user = db.query(User.id).filter(User.email == user_data.email).first()
        if db_user:
            logger.info(f"Registration failed: Email already registered: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            role=user_data.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create mechanic profile if role is mechanic
        if user_data.role == "mechanic":
            mechanic = Mechanic(user_id=db_user.id)
            db.add(mechanic)
            db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        
        end_time = time.time()
        logger.info(f"Registration completed for {user_data.email} in {end_time - start_time:.2f} seconds")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserSchema.from_orm(db_user)
        }
        
    except (OperationalError, DatabaseError) as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

@router.post("/login", response_model=Token)
async def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    start_time = time.time()
    logger.info(f"Login request received for email: {user_data.email}")
    
    try:
        # Authenticate user - optimize query to fetch only necessary fields
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, user.hashed_password):
            logger.info(f"Login failed: Incorrect email or password for {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        end_time = time.time()
        logger.info(f"Login completed for {user_data.email} in {end_time - start_time:.2f} seconds")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserSchema.from_orm(user)
        }
        
    except (OperationalError, DatabaseError) as e:
        logger.error(f"Database error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable. Please try again later."
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 401 Unauthorized)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        end_time = time.time()
        logger.info(f"Token generation completed in {end_time - start_time:.2f} seconds")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserSchema.from_orm(user)
        }
        
    except (OperationalError, DatabaseError) as e:
        logger.error(f"Database error during token generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable. Please try again later."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
