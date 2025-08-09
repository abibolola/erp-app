from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    org_id = Column(Integer, ForeignKey("organization.id"))
    role_id = Column(Integer, ForeignKey("role.id"))

    organization = relationship("Organization", back_populates="users")
    role = relationship("Role", back_populates="users")
    leads = relationship("Lead", back_populates="created_by")

