from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt as bcrypt_lib
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User
from config import settings

security = HTTPBearer()

# bcrypt hard limit is 72 bytes — always work at the byte level to avoid passlib interference
_BCRYPT_ROUNDS = 10
_MAX_BYTES     = 71  # use 71 to stay safely under bcrypt's 72-byte hard cap

def _to_bytes(password: str) -> bytes:
    """Encode password to UTF-8 and hard-truncate to 71 bytes."""
    return password.encode("utf-8")[:_MAX_BYTES]

def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt, bypassing passlib to avoid the 72-byte limit error."""
    pw_bytes = _to_bytes(password)
    salt = bcrypt_lib.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt_lib.hashpw(pw_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    pw_bytes   = _to_bytes(plain_password)
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt_lib.checkpw(pw_bytes, hash_bytes)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
