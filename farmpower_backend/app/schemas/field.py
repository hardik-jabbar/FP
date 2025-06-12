from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any # Any for GeoJSON coordinates for now
from datetime import datetime

from .user import User as UserSchema # For embedding owner info
from .land_usage_plan import LandUsagePlanSchema # Import the LandUsagePlan schema

# Basic GeoJSON structure (can be more specific if needed)
# For simplicity, allowing any dict. For stricter validation, define specific GeoJSON Pydantic models.
GeoJsonCoordinates = Dict[str, Any]

class FieldBase(BaseModel):
    name: str = Field(..., min_length=3, example="Main North Field")
    coordinates: GeoJsonCoordinates = Field(..., example={"type": "Polygon", "coordinates": [[[-73.985130, 40.758896], [-73.986900, 40.756350], [-73.983330, 40.755000], [-73.985130, 40.758896]]]})
    area_hectares: Optional[float] = Field(None, gt=0, example=10.5)
    crop_info: Optional[str] = Field(None, example="Currently fallow")
    # soil_type will be added later or via a different update mechanism

class FieldCreate(FieldBase):
    pass

class FieldUpdate(BaseModel): # All fields optional for update
    name: Optional[str] = Field(None, min_length=3)
    coordinates: Optional[GeoJsonCoordinates] = None
    area_hectares: Optional[float] = Field(None, gt=0)
    crop_info: Optional[str] = None
    # soil_type update might be handled differently

class FieldSchema(FieldBase): # For responses, renamed from Field to avoid conflict with model name
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    soil_type: Optional[str] = None # Include soil_type in response

    owner: UserSchema # Embed owner information
    land_usage_plans: List[LandUsagePlanSchema] = [] # List of associated plans

    class Config:
        from_attributes = True # Pydantic V2 (formerly orm_mode)
