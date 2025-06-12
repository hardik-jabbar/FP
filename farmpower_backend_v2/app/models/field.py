from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from ..core.db import Base

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)

    # Store coordinates as GeoJSON structure, e.g., for a polygon:
    # { "type": "Polygon", "coordinates": [[[lon1, lat1], [lon2, lat2], ...]] }
    coordinates = Column(JSON, nullable=False)

    area_hectares = Column(Float, nullable=True)
    crop_info = Column(String, nullable=True) # Current crop or general notes
    soil_type = Column(String, nullable=True) # Placeholder, to be populated later

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False) # Added index
    owner = relationship("User", back_populates="fields")

    # Relationship to LandUsagePlan (one-to-many: one Field can have many Plans)
    land_usage_plans = relationship("LandUsagePlan", back_populates="field", cascade="all, delete-orphan")

    # Relationship to Crop entries (many-to-many through association, or simple one-to-many if a field has one "current" crop entry)
    # For now, assuming a Field can have multiple crop entries/history linked to it.
    crop_entries = relationship("Crop", back_populates="field", cascade="all, delete-orphan") # Crop model will have a field_id FK

    def __repr__(self):
        return f"<Field(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
