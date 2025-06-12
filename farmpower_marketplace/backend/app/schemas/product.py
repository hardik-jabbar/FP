from pydantic import BaseModel
from typing import Optional, Dict, Any

class ProductBase(BaseModel):
    title: str
    price: float
    location: str
    image_url: Optional[str] = None
    description: Optional[str] = None

class TractorBase(ProductBase):
    specs: Optional[Dict[str, Any]] = None

class TractorCreate(TractorBase):
    pass

class Tractor(TractorBase):
    id: int

    class Config:
        orm_mode = True

class PartBase(ProductBase):
    brand: Optional[str] = None
    part_type: Optional[str] = None # 'type' is a reserved keyword

class PartCreate(PartBase):
    pass

class Part(PartBase):
    id: int

    class Config:
        orm_mode = True 