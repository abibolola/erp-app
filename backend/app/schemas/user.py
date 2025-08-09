from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    org_id: Optional[int] = None
    role_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool

    model_config = {
        "from_attributes": True
    }
