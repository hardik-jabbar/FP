from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict # Any/Dict for plan_details in minimal Field
from datetime import datetime

from .user import UserSchema # For embedding owner info

# Minimal Field schema to avoid circular dependencies if full FieldSchema imports CropSchema
class MinimalFieldSchema(BaseModel):
    id: int
    name: str
    # Add other essential fields if needed, but keep it minimal

    class Config:
        from_attributes = True

class CropBase(BaseModel):
    name: str = Field(..., example="Corn", min_length=2, max_length=100)
    crop_variety: Optional[str] = Field(None, example="Yellow Dent #2", max_length=100)

    seed_cost_per_hectare: float = Field(..., gt=0, example=120.50)
    fertilizer_cost_per_hectare: float = Field(..., gt=0, example=180.75)
    pesticide_cost_per_hectare: Optional[float] = Field(0.0, ge=0, example=60.0)
    machinery_cost_per_hectare: Optional[float] = Field(0.0, ge=0, example=75.25)
    labor_cost_per_hectare: Optional[float] = Field(0.0, ge=0, example=90.0)
    other_costs_per_hectare: Optional[float] = Field(0.0, ge=0, example=30.50)

    expected_yield_per_hectare: float = Field(..., gt=0, example=12.0)
    yield_unit: str = Field("tonnes", example="tonnes", min_length=1, max_length=20)
    market_price_per_unit: float = Field(..., gt=0, example=190.0)

    notes: Optional[str] = Field(None, example="Standard planting for this region.")
    field_id: Optional[int] = Field(None, description="Optional ID of the field this crop data is associated with.")

class CropCreate(CropBase):
    pass

class CropUpdate(BaseModel): # All fields are optional for update
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    crop_variety: Optional[str] = Field(None, max_length=100)
    seed_cost_per_hectare: Optional[float] = Field(None, gt=0)
    fertilizer_cost_per_hectare: Optional[float] = Field(None, gt=0)
    pesticide_cost_per_hectare: Optional[float] = Field(None, ge=0)
    machinery_cost_per_hectare: Optional[float] = Field(None, ge=0)
    labor_cost_per_hectare: Optional[float] = Field(None, ge=0)
    other_costs_per_hectare: Optional[float] = Field(None, ge=0)
    expected_yield_per_hectare: Optional[float] = Field(None, gt=0)
    yield_unit: Optional[str] = Field(None, min_length=1, max_length=20)
    market_price_per_unit: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None
    field_id: Optional[int] = None # Allow changing or unsetting field_id

# For responses
class CropSchema(CropBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    owner: UserSchema
    field: Optional[MinimalFieldSchema] = None # Embed minimal field info if linked

    class Config:
        from_attributes = True

# Schema for Profit Calculation Result
class ProfitCalculationResult(BaseModel):
    crop_name: str
    crop_variety: Optional[str] = None
    total_revenue_per_hectare: float
    total_costs_per_hectare: float
    profit_or_loss_per_hectare: float
    # profit_margin_percentage: float # Calculated if needed, often derived in frontend or a specific report

    cost_breakdown: Dict[str, float] = Field(..., example={
        "seed": 120.50, "fertilizer": 180.75, "pesticide": 60.0,
        "machinery": 75.25, "labor": 90.0, "other": 30.50
    })
    revenue_details: Dict[str, Any] = Field(..., example={
        "expected_yield": 12.0, "yield_unit": "tonnes", "market_price_per_unit": 190.0
    })
