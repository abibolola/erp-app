from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Permission(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)

    roles = relationship("Role", secondary="rolepermission", back_populates="permissions")