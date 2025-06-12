from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.dependencies import get_current_active_user
from ..models.user import User as UserModel
from ..schemas.message import MessageSchema, MessageCreate, ConversationSchema
from ..services import message_service, user_service # user_service to check recipient existence

router = APIRouter(
    prefix="/messages",
    tags=["Messaging"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
async def send_new_message(
    message_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Send a new message to another user.
    `sender_id` is automatically set to the current authenticated user.
    """
    if current_user.id == message_in.recipient_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send messages to yourself.")

    # Check if recipient exists
    recipient_user = user_service.get_user_by_id(db, user_id=message_in.recipient_id)
    if not recipient_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient user not found.")

    return message_service.create_message(db=db, message_in=message_in, sender_id=current_user.id)

@router.get("/conversations/", response_model=List[ConversationSchema])
async def get_my_conversations(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get a list of all conversations for the current user,
    showing the other participant and the last message.
    """
    return message_service.get_conversations_for_user(db=db, user_id=current_user.id)

@router.get("/conversation/{conversation_id}", response_model=List[MessageSchema])
async def get_messages_in_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200) # Default 50 messages, max 200
):
    """
    Get messages for a specific conversation ID.
    The current user must be a participant in the conversation.
    Messages are returned oldest first.
    """
    # Authorization is implicitly handled by get_messages_for_conversation in service
    # as it filters by user_id being sender or recipient within that conversation_id.
    # However, an explicit check here could be an additional layer.
    messages = message_service.get_messages_for_conversation(
        db=db, conversation_id=conversation_id, user_id=current_user.id, skip=skip, limit=limit
    )
    if not messages and skip == 0: # If no messages and it's the first page, maybe convo doesn't exist for user
        # Check if conversation_id is valid for this user by trying to parse participants
        try:
            ids_str = conversation_id.split('-')
            participant_ids = [int(id_str) for id_str in ids_str]
            if current_user.id not in participant_ids:
                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this conversation.")
        except (ValueError, IndexError): # Catch potential errors from malformed conversation_id
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation ID format.")
        # If user is part of convo but no messages, return empty list (which it does)

    return messages

@router.post("/conversation/{conversation_id}/read", status_code=status.HTTP_200_OK)
async def mark_conversation_as_read(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Mark all messages in a specific conversation as read by the current user.
    """
    # Authorization: ensure current_user is part of this conversation_id
    try:
        ids_str = conversation_id.split('-')
        participant_ids = [int(id_str) for id_str in ids_str]
        if current_user.id not in participant_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to mark messages in this conversation as read.")
    except (ValueError, IndexError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation ID format.")

    updated_count = message_service.mark_messages_as_read(
        db=db, conversation_id=conversation_id, recipient_id=current_user.id
    )
    return {"message": f"{updated_count} messages marked as read."}
