from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from ..core.db import Base

class LandUsagePlan(Base):
    __tablename__ = "land_usage_plans"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False, index=True) # Added index

    plan_name = Column(String, nullable=False, index=True)
    # e.g., "Spring Planting 2024", "Soil Enrichment Phase 1"

    plan_details = Column(JSON, nullable=True)
    # Flexible JSON to store details like:
    # {"crop_rotation": ["Corn", "Soybean"], "irrigation_schedule": "daily", "fertilizer_plan": "organic_compost"}
    # {"soil_preparation": "No-till", "pest_control_measures": ["Ladybugs", "Neem Oil"]}

    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Added updated_at

    # Relationship back to Field
    field = relationship("Field", back_populates="land_usage_plans")

    def __repr__(self):
        return f"<LandUsagePlan(id={self.id}, name='{self.plan_name}', field_id={self.field_id})>"
