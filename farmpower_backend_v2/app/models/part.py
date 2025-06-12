from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from ..core.db import Base

class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=False)  # e.g., "Engine", "Filters", "Tyres", "Hydraulics"
    part_number = Column(String(100), index=True, nullable=True)
    brand = Column(String(100), index=True, nullable=True)  # Brand of the part itself, e.g., "Bosch", "Fleetguard"

    # Compatibility info stored as JSON arrays of strings
    tractor_brand_compatibility = Column(JSON, nullable=True, default=lambda: []) # e.g., ["John Deere", "Massey Ferguson"]
    tractor_model_compatibility = Column(JSON, nullable=True, default=lambda: []) # e.g., ["John Deere 5055E", "MF 241 DI"]

    condition = Column(String(50), index=True, nullable=False)  # e.g., "New", "Used - Good", "Refurbished"
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    location = Column(String(255), nullable=True) # Seller's location for the part

    image_urls = Column(JSON, nullable=True, default=lambda: [])

    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("User", back_populates="parts_listed")

    def __repr__(self):
        return f"<Part(id={self.id}, name='{self.name}', seller_id={self.seller_id})>"
