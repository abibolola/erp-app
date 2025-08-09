from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int
    username: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str