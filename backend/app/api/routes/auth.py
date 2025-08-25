from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import LoginRequest, Token, TokenResponse, RefreshRequest
from app.db.session import get_db
from app.models.user import User
from app.services import auth_service
from app.core.security import (
    get_current_user, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    generate_csrf_token,
    require_csrf_token
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut)
async def register_user(
    user: UserCreate, 
    response: Response,
    db: Session = Depends(get_db),
    x_client_type: Optional[str] = Header(None)
):
    """
    Register a new user with appropriate auth response based on client type
    """
    email_normalized = user.email.lower()
    existing = db.query(User).filter(func.lower(User.email) == email_normalized).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth_service.get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=email_normalized,
        password_hash=hashed_password,
        org_id=user.org_id,
        role_id=user.role_id,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create tokens
    access_token = create_access_token({
        "sub": new_user.username,
        "user_id": new_user.id
    })
    refresh_token = create_refresh_token({
        "sub": new_user.username,
        "user_id": new_user.id
    })
    
    # Default to web behavior if not specified
    client_type = x_client_type or 'web'
    
    if client_type.lower() == 'web':
        # Set secure httpOnly cookies for web browsers
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        
        # Set CSRF token
        csrf_token = generate_csrf_token()
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,  # JavaScript needs to read this
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
    
    return new_user

@router.post("/login")
async def login_user(
    credentials: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    x_client_type: Optional[str] = Header(None)
):
    """
    Login endpoint that supports both:
    1. Web browsers (returns cookies) - X-Client-Type: web
    2. API clients (returns JSON with tokens) - X-Client-Type: mobile/api
    
    Defaults to web (cookie-based) for backward compatibility
    """
    email_normalized = credentials.email.lower()
    user = db.query(User).filter(func.lower(User.email) == email_normalized).first()
    
    if not user or not auth_service.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create tokens
    access_token = create_access_token({
        "sub": user.username,
        "user_id": user.id
    })
    refresh_token = create_refresh_token({
        "sub": user.username,
        "user_id": user.id
    })
    
    # Default to web behavior if not specified
    client_type = x_client_type or 'web'
    
    if client_type.lower() == 'web':
        # Set secure httpOnly cookies for web browsers
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        
        # Set CSRF token for web clients
        csrf_token = generate_csrf_token()
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,  # JavaScript needs to read this
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        
        return {
            "message": "Login successful",
            "user": UserOut.from_orm(user)
        }
    else:
        # Return tokens in response body for API/mobile clients
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": UserOut.from_orm(user)
        }

@router.post("/refresh")
async def refresh_tokens(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    token_data = verify_token(refresh_token, token_type="refresh")
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create new access token
    new_access_token = create_access_token({
        "sub": user.username,
        "user_id": user.id
    })
    
    # Update access token cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"message": "Token refreshed successfully"}

@router.post("/logout")
async def logout_user(response: Response):
    """Logout user by clearing cookies"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="csrf_token")
    
    return {"message": "Logout successful"}

@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return current_user

@router.get("/csrf")
async def get_csrf_token(response: Response):
    """Get CSRF token for forms"""
    csrf_token = generate_csrf_token()
    
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {"csrf_token": csrf_token}
