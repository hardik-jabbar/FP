from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CropProfitRequest(BaseModel):
    """Request model for crop profit calculation."""
    crop_id: str
    field_area_acres: float = Field(..., gt=0)
    seed_cost_per_acre: float = Field(..., ge=0)
    fertilizer_cost_per_acre: float = Field(..., ge=0)
    pesticide_cost_per_acre: float = Field(..., ge=0)
    labor_cost_total: float = Field(..., ge=0)
    other_costs_total: float = Field(..., ge=0)
    expected_yield_per_acre: float = Field(..., gt=0)
    market_price_per_unit: float = Field(..., gt=0)

class CropProfitResponse(BaseModel):
    """Response model for crop profit calculation."""
    total_cost: float
    revenue: float
    profit: float
    profit_margin: float

class CropCalculationHistory(BaseModel):
    """Model for storing and retrieving crop calculations."""
    crop_type: str
    field_area: float
    total_cost: float
    revenue: float
    profit: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True 