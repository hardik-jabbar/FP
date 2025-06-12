from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from ..core.db import Base

class LandUsagePlan(Base):
    __tablename__ = "land_usage_plans"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)

    plan_name = Column(String, nullable=False, index=True)
    # e.g., "Spring Planting 2024", "Soil Enrichment Phase 1"

    plan_details = Column(JSON, nullable=True)
    # Flexible JSON to store details like:
    # {"crop": "Corn", "variety": "Sweet Corn XYZ", "planting_density": "30000 seeds/acre"}
    # {"fertilizer_schedule": [{"date": "2024-03-15", "type": "Nitrogen X", "amount_kg_ha": 50}]}
    # {"tillage_method": "No-till", "cover_crop": "Clover"}

    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    # No updated_at for this version, can be added if plans are mutable often

    # Relationship back to Field
    field = relationship("Field", back_populates="land_usage_plans")

    def __repr__(self):
        return f"<LandUsagePlan(id={self.id}, name='{self.plan_name}', field_id={self.field_id})>"
