from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..core.db import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # e.g., "Corn", "Soybeans"
    crop_variety = Column(String, nullable=True)  # e.g., "Yellow Dent #2", "Roundup Ready"

    # Costs per hectare
    seed_cost_per_hectare = Column(Float, nullable=False)
    fertilizer_cost_per_hectare = Column(Float, nullable=False)
    pesticide_cost_per_hectare = Column(Float, nullable=True, default=0.0)
    machinery_cost_per_hectare = Column(Float, nullable=True, default=0.0)  # Fuel, maintenance, rental
    labor_cost_per_hectare = Column(Float, nullable=True, default=0.0)
    other_costs_per_hectare = Column(Float, nullable=True, default=0.0) # e.g., irrigation, insurance

    # Yield and Revenue
    expected_yield_per_hectare = Column(Float, nullable=False)  # In units like tonnes or bushels
    yield_unit = Column(String, nullable=False, default="tonnes")  # "bushels", "kg", etc.
    market_price_per_unit = Column(Float, nullable=False)  # Price for one unit of yield_unit

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    # Optional link to a specific field where this crop might be planned or grown
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True) # User who created/owns this crop data

    # Relationships
    owner = relationship("User", back_populates="crops")
    field = relationship("Field", back_populates="crop_entries") # Optional link

    def __repr__(self):
        return f"<Crop(id={self.id}, name='{self.name}', user_id={self.user_id})>"
