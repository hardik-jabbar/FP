from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class LandUsagePlanBase(BaseModel):
    plan_name: str = Field(..., min_length=3, example="Spring Planting 2024")
    plan_details: Optional[Dict[str, Any]] = Field(None, example={"crop": "Corn", "fertilizer": "Urea"})
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class LandUsagePlanCreate(LandUsagePlanBase):
    pass # field_id will be a path parameter or set in service

class LandUsagePlanUpdate(BaseModel): # All fields optional for update
    plan_name: Optional[str] = Field(None, min_length=3)
    plan_details: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class LandUsagePlanSchema(LandUsagePlanBase): # For responses
    id: int
    field_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None # Match model if added

    class Config:
        from_attributes = True # Pydantic V2 (orm_mode)
