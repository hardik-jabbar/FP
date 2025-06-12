from pydantic import BaseModel, Field
from typing import Optional, List, Any # Any for minimal schemas if needed
from datetime import datetime

from ..models.service_booking import ServiceStatus # Import the enum
from .user import UserSchema # For customer and service_provider
# For TractorSchema, import a minimal version or use Any to avoid circular deps initially
# from .tractor import TractorSchema # Full schema might be too large or cause issues

# Minimal Tractor Schema for embedding in ServiceBooking response
class MinimalTractorSchema(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None

    class Config:
        from_attributes = True

class ServiceBookingBase(BaseModel):
    tractor_id: Optional[int] = Field(None, description="ID of the tractor needing service, if applicable.")
    service_type: str = Field(..., example="600-hour Maintenance", description="Type of service requested.")
    description: Optional[str] = Field(None, example="Tractor making strange noises from engine bay.")
    scheduled_date: datetime = Field(..., example="2024-08-15T10:00:00Z") # Datetime for scheduling
    # status is usually set by the system or provider, not directly by user on creation
    service_provider_id: Optional[int] = Field(None, description="Preferred or assigned service provider ID.")
    notes: Optional[str] = Field(None, example="User mentioned urgency.")

class ServiceBookingCreate(ServiceBookingBase):
    # Status will be defaulted in the model or service layer, not set by user on create.
    pass

class ServiceBookingUpdate(BaseModel): # All fields optional for update
    tractor_id: Optional[int] = None
    service_type: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[ServiceStatus] = None # Provider or system might update this
    service_provider_id: Optional[int] = None
    notes: Optional[str] = None

class ServiceBookingSchema(ServiceBookingBase): # For responses
    id: int
    user_id: int # ID of the customer who booked
    status: ServiceStatus # Ensure status is part of the response
    created_at: datetime
    updated_at: datetime

    customer: UserSchema # Embed customer details
    tractor: Optional[MinimalTractorSchema] = None # Embed minimal tractor details if linked
    service_provider: Optional[UserSchema] = None # Embed provider details if assigned

    class Config:
        from_attributes = True # Pydantic V2 (orm_mode)
