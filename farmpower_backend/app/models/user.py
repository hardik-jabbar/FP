import enum
from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, Boolean, DateTime # Import DateTime
from sqlalchemy.orm import relationship # Import relationship
from ..core.db import Base # Adjusted import path

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
    role = Column(SQLAlchemyEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False) # For email/OTP verification

    # Fields for OTP/email verification
    otp_secret = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)

    # Relationship to Tractors
    tractors = relationship("Tractor", back_populates="owner", cascade="all, delete-orphan")

    # Relationship to Fields
    fields = relationship("Field", back_populates="owner", cascade="all, delete-orphan")

    # Relationship to Crops
    crops = relationship("Crop", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
