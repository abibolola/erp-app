from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Lead(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    status = Column(String, default="new")  # e.g., new, contacted, converted
    notes = Column(Text, nullable=True)

    created_by_id = Column(Integer, ForeignKey("user.id"))
    created_by = relationship("User", back_populates="leads")
