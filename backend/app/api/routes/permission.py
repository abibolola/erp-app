from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.permission import PermissionOut
from app.models.permission import Permission
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.get("/", response_model=list[PermissionOut])
def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    return db.query(Permission).all()
