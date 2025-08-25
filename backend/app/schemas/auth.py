from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int
    username: str
    token_type: Optional[str] = "access"  # Add this field if missing

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    message: str
    user: Optional[dict] = None

class RefreshRequest(BaseModel):
    refresh_token: str