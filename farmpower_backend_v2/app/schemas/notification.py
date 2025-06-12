from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from ..models.notification import NotificationType # Import the enum

class NotificationBase(BaseModel):
    # user_id is not in Base as it's usually set by the system/service based on context
    title: str = Field(..., example="Service Reminder")
    message: str = Field(..., example="Your tractor service is due next week.")
    type: NotificationType = Field(default=NotificationType.GENERAL_INFO)
    related_entity_type: Optional[str] = Field(None, example="service_booking")
    related_entity_id: Optional[int] = Field(None, example=101)

class NotificationCreateInternal(NotificationBase): # For service layer use
    user_id: int # Explicitly set who the notification is for

# For responses to the user
class NotificationSchema(BaseModel):
    id: int
    title: str
    message: str
    type: NotificationType
    is_read: bool
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
