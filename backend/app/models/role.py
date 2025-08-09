from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class Role(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    is_default = Column(Boolean, default=False)

    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="rolepermission", back_populates="roles")