from sqlalchemy import Column, Integer, ForeignKey, Table
from app.models.base import Base

RolePermission = Table(
    "rolepermission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("role.id")),
    Column("permission_id", Integer, ForeignKey("permission.id")),
)