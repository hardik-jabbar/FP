from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON # Assuming Float for area
from sqlalchemy.orm import relationship
from ..core.db import Base
# LandUsagePlan will be imported after its definition if needed for type hinting,
# but SQLAlchemy handles relationships via strings.

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)

    # Store coordinates as GeoJSON structure, e.g., for a polygon:
    # { "type": "Polygon", "coordinates": [[[lon1, lat1], [lon2, lat2], ...]] }
    coordinates = Column(JSON, nullable=False)

    area_hectares = Column(Float, nullable=True) # Can be calculated or user-provided
    crop_info = Column(String, nullable=True) # Simple text field for current crop
    soil_type = Column(String, nullable=True) # To be populated later via external API or user input

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="fields")

    # Relationship to LandUsagePlan
    land_usage_plans = relationship("LandUsagePlan", back_populates="field", cascade="all, delete-orphan")

    # Relationship to Crop entries (optional link from Crop model to a specific field)
    crop_entries = relationship("Crop", back_populates="field")

    def __repr__(self):
        return f"<Field(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
