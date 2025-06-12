from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Assuming UserSchema and LandUsagePlanSchema are defined
from .user import UserSchema
from .land_usage_plan import LandUsagePlanSchema

# For GeoJSON coordinates, a simple dict is used.
# For production, consider a more specific Pydantic model for GeoJSON validation.
GeoJsonStructure = Dict[str, Any]

class FieldBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Main North Field")
    # Example GeoJSON for a simple polygon
    coordinates: GeoJsonStructure = Field(..., example={
        "type": "Polygon",
        "coordinates": [[
            [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]
        ]]
    })
    area_hectares: Optional[float] = Field(None, gt=0, example=12.5)
    crop_info: Optional[str] = Field(None, max_length=255, example="Currently planted with Winter Wheat")
    # soil_type is managed separately or via different mechanism, not in base create/update directly by user initially

class FieldCreate(FieldBase):
    pass

class FieldUpdate(BaseModel): # All fields optional for update
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    coordinates: Optional[GeoJsonStructure] = None
    area_hectares: Optional[float] = Field(None, gt=0)
    crop_info: Optional[str] = Field(None, max_length=255)
    soil_type: Optional[str] = Field(None, max_length=100) # Allow updating soil_type if needed

class FieldSchema(FieldBase): # For responses
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    soil_type: Optional[str] = None # Include in response

    owner: UserSchema # Embed owner information
    land_usage_plans: List[LandUsagePlanSchema] = [] # List of associated plans, default empty

    class Config:
        from_attributes = True # Pydantic V2 (orm_mode)
