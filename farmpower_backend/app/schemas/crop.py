from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .user import User as UserSchema # For embedding owner info
# from .field import FieldSchema # Only if embedding detailed field info, otherwise field_id is enough

class CropBase(BaseModel):
    name: str = Field(..., example="Corn")
    crop_variety: Optional[str] = Field(None, example="Yellow Dent #2")

    seed_cost_per_hectare: float = Field(..., gt=0, example=100.0)
    fertilizer_cost_per_hectare: float = Field(..., gt=0, example=150.0)
    pesticide_cost_per_hectare: Optional[float] = Field(0.0, ge=0, example=50.0)
    machinery_cost_per_hectare: Optional[float] = Field(0.0, ge=0, example=70.0)
    labor_cost_per_hectare: Optional[float] = Field(0.0, ge=0, example=80.0)
    other_costs_per_hectare: Optional[float] = Field(0.0, ge=0, example=20.0)

    expected_yield_per_hectare: float = Field(..., gt=0, example=10.0)
    yield_unit: str = Field("tonnes", example="tonnes")
    market_price_per_unit: float = Field(..., gt=0, example=200.0)

    field_id: Optional[int] = Field(None, description="Optional ID of the field this crop is associated with")

class CropCreate(CropBase):
    pass

class CropUpdate(BaseModel): # All fields optional for update
    name: Optional[str] = None
    crop_variety: Optional[str] = None
    seed_cost_per_hectare: Optional[float] = Field(None, gt=0)
    fertilizer_cost_per_hectare: Optional[float] = Field(None, gt=0)
    pesticide_cost_per_hectare: Optional[float] = Field(None, ge=0)
    machinery_cost_per_hectare: Optional[float] = Field(None, ge=0)
    labor_cost_per_hectare: Optional[float] = Field(None, ge=0)
    other_costs_per_hectare: Optional[float] = Field(None, ge=0)
    expected_yield_per_hectare: Optional[float] = Field(None, gt=0)
    yield_unit: Optional[str] = None
    market_price_per_unit: Optional[float] = Field(None, gt=0)
    field_id: Optional[int] = None


class CropSchema(CropBase): # For responses, changed name from Crop to CropSchema
    id: int
    user_id: int # Expose user_id who owns this crop entry
    created_at: datetime
    updated_at: datetime

    owner: UserSchema # Embed owner information
    # field: Optional[FieldSchema] = None # If you want to embed full field details

    class Config:
        from_attributes = True # Pydantic V2 (formerly orm_mode)

# Schema for Profit Calculation Result
class ProfitCalculationResult(BaseModel):
    crop_name: str
    crop_variety: Optional[str] = None
    total_revenue_per_hectare: float
    total_costs_per_hectare: float
    profit_or_loss_per_hectare: float
    profit_margin_percentage: float = Field(..., ge=0) # Can be > 100 if costs are negative (subsidies) or very low

    # Optional breakdown
    breakdown_costs: Optional[dict] = None
    breakdown_revenue: Optional[dict] = None
