from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from .user import UserSchema # For embedding sender info

class MessageBase(BaseModel):
    recipient_id: int = Field(..., description="ID of the message recipient.")
    content: str = Field(..., min_length=1, max_length=2000, example="Hello, is this part still available?")

class MessageCreate(MessageBase):
    pass

class MessageSchema(BaseModel): # For responses
    id: int
    sender_id: int
    recipient_id: int
    conversation_id: str
    content: str
    created_at: datetime
    is_read_by_recipient: bool

    sender: UserSchema # Embed sender's public info

    class Config:
        from_attributes = True

# Schema for listing conversations
class ConversationSchema(BaseModel):
    conversation_id: str
    other_user: UserSchema # The other user in the conversation
    last_message_content: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0

    class Config:
        from_attributes = True # If built from ORM objects with these properties calculated by service
