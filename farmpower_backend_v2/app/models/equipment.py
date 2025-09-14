from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from ..database import Base

class EquipmentType(str, PyEnum):
    TRACTOR = "tractor"
    HARVESTER = "harvester"
    PLANTER = "planter"
    SPRAYER = "sprayer"
    CULTIVATOR = "cultivator"
    OTHER = "other"

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)
    description = Column(String)
    manufacturer = Column(String, index=True)
    model = Column(String)
    year = Column(Integer)
    hours_used = Column(Float)
    price_per_day = Column(Float)
    is_available = Column(Boolean, default=True)
    location = Column(String)
    image_url = Column(String)
    
    # Owner information
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="equipment")
    
    # Booking related
    bookings = relationship("Booking", back_populates="equipment")
    
    # Maintenance records
    maintenance_records = relationship("MaintenanceRecord", back_populates="equipment")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    equipment = relationship("Equipment", back_populates="maintenance_records")
    
    service_date = Column(DateTime)
    description = Column(String)
    cost = Column(Float)
    next_service_date = Column(DateTime)
    technician_notes = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    equipment = relationship("Equipment", back_populates="bookings")
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="bookings")
    
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_price = Column(Float)
    status = Column(String)  # pending, confirmed, cancelled, completed
    payment_status = Column(String)  # pending, paid, refunded
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)