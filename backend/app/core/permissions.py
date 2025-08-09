from fastapi import Depends, HTTPException, status
from functools import wraps
from typing import Callable
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.user import User
from app.db.session import get_db

def requires_permission(permission_name: str):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), **kwargs):
            # Fetch user's permissions from DB
            role = db.query(current_user.role).first()
            if not role:
                raise HTTPException(status_code=403, detail="No role assigned")

            role_permissions = [perm.name for perm in role.permissions]
            if permission_name not in role_permissions:
                raise HTTPException(status_code=403, detail=f"Missing permission: {permission_name}")

            return await func(*args, current_user=current_user, db=db, **kwargs)
        return wrapper
    return decorator
