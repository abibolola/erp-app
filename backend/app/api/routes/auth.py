from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import LoginRequest, Token
from app.db.session import get_db
from app.models.user import User
from app.services import auth_service
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
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
    return new_user

@router.post("/login", response_model=Token)
def login_user(credentials: LoginRequest, db: Session = Depends(get_db)):
    email_normalized = credentials.email.lower()
    user = db.query(User).filter(func.lower(User.email) == email_normalized).first()
    if not user or not auth_service.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth_service.create_access_token({
        "sub": user.username,
        "user_id": user.id,
    })
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
