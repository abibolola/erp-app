from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.role import RoleOut
from app.models.role import Role
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/", response_model=list[RoleOut])
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    return db.query(Role).all()
