from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

# Import a minimal User schema for owner representation
from .user import User as UserSchema # Assuming User schema includes id, email, full_name

class TractorBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, example="John Deere 5075E")
    brand: str = Field(..., max_length=50, example="John Deere")
    model: str = Field(..., max_length=50, example="5075E")
    year: int = Field(..., gt=1900, lt=datetime.now().year + 2, example=2020) # Year greater than 1900 and not too far in future
    price: float = Field(..., gt=0, example=25000.00)
    location: str = Field(..., max_length=200, example="Nagpur, Maharashtra")
    description: Optional[str] = Field(None, max_length=1000, example="Well-maintained tractor, single owner.")
    horsepower: Optional[int] = Field(None, gt=0, example=75)
    condition: Optional[str] = Field(None, max_length=50, example="Used - Good")
    image_urls: Optional[List[HttpUrl]] = Field(None, example=["http://example.com/image1.jpg"])

class TractorCreate(TractorBase):
    pass

class TractorUpdate(BaseModel): # All fields optional for update
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, gt=1900, lt=datetime.now().year + 2)
    price: Optional[float] = Field(None, gt=0)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    horsepower: Optional[int] = Field(None, gt=0)
    condition: Optional[str] = Field(None, max_length=50)
    image_urls: Optional[List[HttpUrl]] = None


class TractorInDBBase(TractorBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Pydantic V2 (formerly orm_mode)

class Tractor(TractorInDBBase): # Full response model
    owner: UserSchema # Embed owner information (using the User schema from user.py)
    # image_urls are already in TractorBase, so they'll be here too.
    pass
