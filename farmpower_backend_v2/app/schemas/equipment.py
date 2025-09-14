from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class EquipmentType(str, Enum):
    TRACTOR = "tractor"
    HARVESTER = "harvester"
    PLANTER = "planter"
    SPRAYER = "sprayer"
    CULTIVATOR = "cultivator"
    OTHER = "other"

class MaintenanceRecordBase(BaseModel):
    service_date: datetime
    description: str
    cost: float
    next_service_date: Optional[datetime] = None
    technician_notes: Optional[str] = None

class MaintenanceRecordCreate(MaintenanceRecordBase):
    equipment_id: int

class MaintenanceRecord(MaintenanceRecordBase):
    id: int
    equipment_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EquipmentBase(BaseModel):
    name: str
    type: EquipmentType
    description: str
    manufacturer: str
    model: str
    year: int
    hours_used: float
    price_per_day: float
    location: str
    image_url: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    pass

class Equipment(EquipmentBase):
    id: int
    owner_id: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
    maintenance_records: List[MaintenanceRecord] = []

    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    equipment_id: int
    start_date: datetime
    end_date: datetime

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: int
    total_price: float
    status: str
    payment_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EquipmentFilter(BaseModel):
    type: Optional[EquipmentType] = None
    manufacturer: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    location: Optional[str] = None
    available_from: Optional[datetime] = None
    available_to: Optional[datetime] = None