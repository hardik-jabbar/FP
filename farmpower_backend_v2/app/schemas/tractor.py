from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Assuming UserSchema is already defined in app.schemas.user
from .user import UserSchema

# Base schema for tractor data
class TractorBase(BaseModel):
    name: str
    brand: str
    model: str
    year: int
    price: float
    location: str
    description: Optional[str] = None
    horsepower: Optional[int] = None
    condition: Optional[str] = None
    image_urls: List[str] = []

# Schema for creating a new tractor
class TractorCreate(TractorBase):
    pass

# Schema for updating an existing tractor
class TractorUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    location: Optional[str] = None
    description: Optional[str] = None
    horsepower: Optional[int] = None
    condition: Optional[str] = None
    image_urls: Optional[List[str]] = None

# Schema for reading/returning tractor data
class TractorSchema(TractorBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    owner: UserSchema # Embed owner information using UserSchema

    class Config:
        from_attributes = True
