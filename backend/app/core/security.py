from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import hmac
import secrets

from app.core.config import settings
from app.schemas.auth import TokenData
from app.db.session import get_db
from app.models.user import User

# OAuth2PasswordBearer for standard OAuth2 flow + cookie fallback
# auto_error=False allows us to handle missing tokens ourselves
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            return None
            
        user_id: int = payload.get("user_id")
        username: str = payload.get("sub")
        
        if user_id is None or username is None:
            return None
            
        # return TokenData(user_id=user_id, username=username, token_type=token_type)
        return TokenData(user_id=user_id, username=username)
    except JWTError:
        return None

def generate_csrf_token() -> str:
    """Generate a CSRF token"""
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, expected: str) -> bool:
    """Verify CSRF token using constant-time comparison"""
    return hmac.compare_digest(token, expected)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),  # Try Authorization header first
    request: Request = None,
    response: Response = None,
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from either:
    1. Authorization: Bearer <token> header (for API clients, mobile apps)
    2. HttpOnly cookie (for web browsers)
    
    This dual approach supports both traditional API clients and secure web apps.
    """
    # Try to get access token from header first (OAuth2 standard)
    access_token = token
    
    # If no header token, try cookie (web browser)
    if not access_token and request:
        access_token = request.cookies.get("access_token")
    
    if not access_token:
        # Try to refresh using refresh token
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify refresh token
        token_data = verify_token(refresh_token, token_type="refresh")
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate new access token
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_access_token = create_access_token({
            "sub": user.username,
            "user_id": user.id
        })
        
        # Set new access token in cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return user
    
    # Verify access token
    token_data = verify_token(access_token, token_type="access")
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def require_csrf_token(request: Request):
    """Verify CSRF token for state-changing operations"""
    csrf_token = request.headers.get("X-CSRF-Token")
    csrf_cookie = request.cookies.get("csrf_token")
    
    if not csrf_token or not csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )
    
    if not verify_csrf_token(csrf_token, csrf_cookie):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )