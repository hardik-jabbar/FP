import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLAlchemyEnum, Text
from sqlalchemy.orm import relationship
from ..core.db import Base

class ServiceStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress" # Added for more granularity
    COMPLETED = "completed"
    CANCELLED_BY_USER = "cancelled_by_user"
    CANCELLED_BY_PROVIDER = "cancelled_by_provider" # Or just CANCELLED

class ServiceBooking(Base):
    __tablename__ = "service_bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True) # The customer booking the service
    tractor_id = Column(Integer, ForeignKey("tractors.id"), nullable=True, index=True) # Optional: if service is for a specific tractor

    service_type = Column(String(255), nullable=False, index=True) # e.g., "Oil Change", "Engine Repair", "Regular Maintenance"
    description = Column(Text, nullable=True) # User's description of the issue or service needed

    scheduled_date = Column(DateTime, nullable=False, index=True)
    status = Column(SQLAlchemyEnum(ServiceStatus), nullable=False, default=ServiceStatus.PENDING, index=True)

    # Optional: If a specific service provider (another User with SERVICE_PROVIDER role) is assigned/chosen
    service_provider_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    notes = Column(Text, nullable=True) # Internal notes by user or provider regarding the booking

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("User", foreign_keys=[user_id], back_populates="services_booked")
    tractor = relationship("Tractor", back_populates="service_history") # Tractor model will need "service_history"
    service_provider = relationship("User", foreign_keys=[service_provider_id], back_populates="services_provided") # User model will need "services_provided"

    def __repr__(self):
        return f"<ServiceBooking(id={self.id}, type='{self.service_type}', status='{self.status.value}', user_id={self.user_id})>"
