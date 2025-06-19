from sqlalchemy import Column, Integer, String, Float, DateTime
from .base import Base, TimestampMixin

class CropCalculation(Base, TimestampMixin):
    """SQLAlchemy model for storing crop calculations."""
    __tablename__ = "crop_calculations"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, nullable=False)
    field_area = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    revenue = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False) 