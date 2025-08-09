from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Organization(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    
    # Optional: allows parent-child org structure
    parent_id = Column(Integer, ForeignKey('organization.id'), nullable=True)

    # Self-referencing relationships
    parent = relationship('Organization', remote_side=[id], backref='children')

    users = relationship("User", back_populates="organization")