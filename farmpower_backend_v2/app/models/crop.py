from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text # Added Text for notes
from sqlalchemy.orm import relationship
from ..core.db import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # e.g., "Corn", "Soybeans"
    crop_variety = Column(String, nullable=True)  # e.g., "Yellow Dent #2", "Pioneer P1197"

    # Costs per hectare
    seed_cost_per_hectare = Column(Float, nullable=False)
    fertilizer_cost_per_hectare = Column(Float, nullable=False)
    pesticide_cost_per_hectare = Column(Float, nullable=True, default=0.0)
    machinery_cost_per_hectare = Column(Float, nullable=True, default=0.0)
    labor_cost_per_hectare = Column(Float, nullable=True, default=0.0)
    other_costs_per_hectare = Column(Float, nullable=True, default=0.0)

    # Yield and Revenue
    expected_yield_per_hectare = Column(Float, nullable=False)
    yield_unit = Column(String, nullable=False, default="tonnes") # e.g., "tonnes", "bushels", "kg"
    market_price_per_unit = Column(Float, nullable=False)

    notes = Column(Text, nullable=True) # Using Text for potentially longer notes

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True) # Added index
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=True, index=True) # Optional link to a specific field
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Relationships
    owner = relationship("User", back_populates="crops")
    field = relationship("Field", back_populates="crop_entries")

    def __repr__(self):
        return f"<Crop(id={self.id}, name='{self.name}', user_id={self.user_id})>"
