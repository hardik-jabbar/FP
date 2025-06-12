from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base schema for part data
class PartBase(BaseModel):
    name: str
    category: str
    brand: Optional[str] = None
    part_number: Optional[str] = None
    price: float
    location: str
    description: Optional[str] = None
    condition: Optional[str] = None
    image_urls: List[str] = []
    stock: int

# Schema for creating a new part
class PartCreate(PartBase):
    pass

# Schema for updating an existing part
class PartUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    part_number: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[str] = None
    image_urls: Optional[List[str]] = None
    stock: Optional[int] = None

# Schema for reading/returning part data
class PartSchema(PartBase):
    id: int
    seller_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
