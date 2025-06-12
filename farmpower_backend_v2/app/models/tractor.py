from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON # Added JSON
from sqlalchemy.orm import relationship
from ..core.db import Base

class Tractor(Base):
    __tablename__ = "tractors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    brand = Column(String, index=True, nullable=False)
    model = Column(String, index=True, nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Float, index=True, nullable=False)
    location = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    horsepower = Column(Integer, nullable=True)
    condition = Column(String, index=True, nullable=True) # e.g., "New", "Used - Good"

    # Store as JSON array of strings. Default to an empty list.
    image_urls = Column(JSON, nullable=True, default=lambda: [])

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    owner = relationship("User", back_populates="tractors")

    # Relationship to ServiceBookings
    service_history = relationship("ServiceBooking", back_populates="tractor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tractor(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
