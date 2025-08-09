from pydantic import BaseModel, EmailStr
from typing import Optional

class LeadBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    status: Optional[str] = "new"
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    pass  # All fields from LeadBase are needed

class LeadUpdate(BaseModel):
    phone: Optional[str]
    status: Optional[str]
    notes: Optional[str]

class LeadOut(LeadBase):
    id: int
    created_by_id: Optional[int]

    class Config:
        from_attributes = True  # Allows ORM → Pydantic
