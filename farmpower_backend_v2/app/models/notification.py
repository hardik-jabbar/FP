import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLAlchemyEnum, Boolean, Text
from sqlalchemy.orm import relationship
from ..core.db import Base

class NotificationType(enum.Enum):
    SERVICE_REMINDER = "service_reminder" # For upcoming service bookings
    SERVICE_STATUS_UPDATE = "service_status_update" # Booking confirmed, completed, cancelled
    WEATHER_ALERT = "weather_alert" # Placeholder for future weather integration
    NEW_MESSAGE = "new_message" # For chat/messaging feature
    PART_INQUIRY_RESPONSE = "part_inquiry_response" # If someone replies to a part listing
    NEW_PART_LISTED = "new_part_listed" # For users watching certain categories/parts (future)
    FIELD_UPDATE = "field_update" # e.g., soil analysis complete
    GENERAL_INFO = "general_info" # General announcements
    ACCOUNT_VERIFIED = "account_verified"
    PASSWORD_RESET_CONFIRMATION = "password_reset_confirmation"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Recipient of the notification

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    type = Column(SQLAlchemyEnum(NotificationType), nullable=False, default=NotificationType.GENERAL_INFO, index=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)

    # Optional: To link notification to a specific entity in the system
    related_entity_type = Column(String(50), nullable=True, index=True)  # e.g., "tractor", "service_booking", "message_thread", "part"
    related_entity_id = Column(Integer, nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    # No updated_at for notifications, they are typically immutable once created, only status changes.

    recipient = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type.value}', is_read={self.is_read})>"
