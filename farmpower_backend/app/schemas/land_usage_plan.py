from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class LandUsagePlanBase(BaseModel):
    plan_name: str = Field(..., example="Spring Planting 2024")
    plan_details: Optional[Dict[str, Any]] = Field(None, example={"crop": "Corn", "variety": "DKC65-95"})
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class LandUsagePlanCreate(LandUsagePlanBase):
    pass

class LandUsagePlanUpdate(BaseModel): # All fields optional for update
    plan_name: Optional[str] = Field(None, example="Spring Planting 2024 (Revised)")
    plan_details: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class LandUsagePlanSchema(LandUsagePlanBase): # For responses
    id: int
    field_id: int # Useful to have in the response
    created_at: datetime

    class Config:
        from_attributes = True # Pydantic V2 (formerly orm_mode)
