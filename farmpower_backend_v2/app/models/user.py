import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, Boolean, DateTime, desc # Import desc
from sqlalchemy.orm import relationship # Ensure relationship is imported
from ..core.db import Base

class UserRole(enum.Enum):
    FARMER = "farmer"
    DEALER = "dealer"
    SERVICE_PROVIDER = "service_provider"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.FARMER) # Default role

    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False, nullable=False) # New field for banning
    is_verified = Column(Boolean, default=False) # For email/OTP verification

    otp_secret = Column(String, nullable=True) # For storing hashed OTP or verification token secret
    otp_expiry = Column(DateTime, nullable=True) # For OTP expiration

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships to other models (will be defined in their respective files)
    tractors = relationship("Tractor", back_populates="owner", cascade="all, delete-orphan")
    fields = relationship("Field", back_populates="owner", cascade="all, delete-orphan")
    crops = relationship("Crop", back_populates="owner", cascade="all, delete-orphan")

    # Example for more complex relationships if ServiceBooking and Part models were defined:
    services_booked = relationship("ServiceBooking", foreign_keys="[ServiceBooking.user_id]", back_populates="customer", cascade="all, delete-orphan")
    services_provided = relationship("ServiceBooking", foreign_keys="[ServiceBooking.service_provider_id]", back_populates="service_provider") # No cascade here, deleting provider doesn't delete bookings
    parts_listed = relationship("Part", back_populates="seller", cascade="all, delete-orphan")

    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan", order_by="desc(Notification.created_at)")

    # Messaging relationships
    sent_messages = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="[Message.recipient_id]", back_populates="recipient", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
