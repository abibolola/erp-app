from pydantic import BaseModel
from typing import List, Optional

class RoleBase(BaseModel):
    name: str
    is_default: Optional[bool] = False

class RoleCreate(RoleBase):
    permissions: Optional[List[int]] = []

class RoleOut(RoleBase):
    id: int
    permissions: List[str] = []

    class Config:
        orm_mode = True
