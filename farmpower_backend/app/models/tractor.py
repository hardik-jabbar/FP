from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON # Added JSON for image_urls
from sqlalchemy.orm import relationship
from ..core.db import Base

class Tractor(Base):
    __tablename__ = "tractors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # e.g., "John Deere 5075E" or a user-friendly title
    brand = Column(String, index=True, nullable=False)
    model = Column(String, index=True, nullable=False) # Model might also be filtered often
    year = Column(Integer, nullable=False)
    price = Column(Float, index=True, nullable=False) # Add index=True
    location = Column(String, index=True, nullable=False) # Add index=True
    description = Column(String, nullable=True)
    horsepower = Column(Integer, nullable=True)
    condition = Column(String, index=True, nullable=True) # Condition might be filtered

    # Image URLs - storing as JSON array of strings.
    # For a more robust solution, consider a separate table for images or specific S3 integration.
    image_urls = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True) # Add index=True
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False) # Index on owner_id often useful
    owner = relationship("User", back_populates="tractors")

    def __repr__(self):
        return f"<Tractor(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
