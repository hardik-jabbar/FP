from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from typing import List, Optional

from ..models.message import Message as MessageModel, generate_conversation_id
from ..models.user import User as UserModel
from ..schemas.message import MessageCreate, ConversationSchema
from ..services.notification_service import notification_service # For creating notifications
from ..schemas.notification import NotificationCreateInternal, NotificationType # For creating notifications

class MessageService:
    def create_message(self, db: Session, message_in: MessageCreate, sender_id: int) -> MessageModel:
        if sender_id == message_in.recipient_id:
            # Decide if self-messaging is allowed or should raise an error
            raise ValueError("Sender and recipient cannot be the same user.")

        conversation_id = generate_conversation_id(sender_id, message_in.recipient_id)

        db_message = MessageModel(
            sender_id=sender_id,
            recipient_id=message_in.recipient_id,
            conversation_id=conversation_id,
            content=message_in.content
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        # Create a notification for the recipient
        recipient = db.query(UserModel).filter(UserModel.id == message_in.recipient_id).first()
        sender = db.query(UserModel).filter(UserModel.id == sender_id).first()
        if recipient and sender: # Ensure users exist
            notification_content = NotificationCreateInternal(
                user_id=recipient.id,
                title=f"New message from {sender.full_name or sender.email}",
                message=f"You have a new message: \"{db_message.content[:50]}...\"", # Preview
                type=NotificationType.NEW_MESSAGE,
                related_entity_type="message_thread", # Or simply "message"
                related_entity_id=db_message.id # Or use conversation_id if linking to the whole convo
            )
            notification_service.create_notification(db=db, notification_in=notification_content)
            # TODO: Here you might also trigger a real-time event via WebSockets to the recipient if they are online.
            # from ..core.socket_manager import sio
            # await sio.emit('new_message', {'conversation_id': conversation_id, 'message': MessageSchema.from_orm(db_message).model_dump()}, room=f'user_{recipient.id}')


        return db_message

    def get_messages_for_conversation(
        self, db: Session, conversation_id: str, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[MessageModel]:
        # Ensure the user_id is part of the conversation to authorize access
        # This check is more robust if done in the router based on current_user
        messages = (
            db.query(MessageModel)
            .filter(MessageModel.conversation_id == conversation_id)
            .filter(or_(MessageModel.sender_id == user_id, MessageModel.recipient_id == user_id))
            .order_by(MessageModel.created_at.asc()) # Typically oldest first in a thread
            .offset(skip)
            .limit(limit)
            .all()
        )
        return messages

    def get_conversations_for_user(self, db: Session, user_id: int) -> List[ConversationSchema]:
        """
        Retrieves a list of conversations for a user, showing the other participant
        and the last message.
        This is a more complex query.
        """
        # Subquery to get the latest message_id for each conversation_id involving the user
        latest_message_subquery = (
            db.query(
                MessageModel.conversation_id,
                func.max(MessageModel.created_at).label("last_message_time")
            )
            .filter(or_(MessageModel.sender_id == user_id, MessageModel.recipient_id == user_id))
            .group_by(MessageModel.conversation_id)
            .subquery("latest_messages_sq")
        )

        # Main query to get the last message and the other user for each conversation
        conversations_data = (
            db.query(
                MessageModel,
                UserModel.id.label("other_user_id"),
                UserModel.full_name.label("other_user_full_name"),
                UserModel.email.label("other_user_email")
            )
            .join(
                latest_message_subquery,
                and_(
                    MessageModel.conversation_id == latest_message_subquery.c.conversation_id,
                    MessageModel.created_at == latest_message_subquery.c.last_message_time
                )
            )
            .join(
                UserModel,
                # Join UserModel on the condition that it's the other participant in the conversation
                or_(
                    and_(MessageModel.sender_id == UserModel.id, MessageModel.recipient_id == user_id),
                    and_(MessageModel.recipient_id == UserModel.id, MessageModel.sender_id == user_id)
                )
            )
            .order_by(desc(MessageModel.created_at)) # Show most recent conversations first
            .all()
        )

        # Process results into ConversationSchema
        # Also count unread messages per conversation
        result_schemas = []
        for last_message, other_user_id, other_user_full_name, other_user_email in conversations_data:
            unread_count = db.query(func.count(MessageModel.id)).filter(
                MessageModel.conversation_id == last_message.conversation_id,
                MessageModel.recipient_id == user_id,
                MessageModel.is_read_by_recipient == False
            ).scalar() or 0

            result_schemas.append(
                ConversationSchema(
                    conversation_id=last_message.conversation_id,
                    other_user={ # Constructing UserSchema manually or use UserSchema.from_orm if UserModel instance is fetched
                        "id": other_user_id,
                        "full_name": other_user_full_name,
                        "email": other_user_email,
                        # These fields are required by UserSchema but might not be relevant/fetched for "other_user" summary
                        "role": UserModel.role.default.value, # Placeholder, ideally fetch actual role or adjust UserSchema
                        "is_active": True, # Placeholder
                        "is_verified": True, # Placeholder
                        "created_at": datetime.min, # Placeholder
                        "updated_at": datetime.min # Placeholder
                    },
                    last_message_content=last_message.content,
                    last_message_at=last_message.created_at,
                    unread_count=unread_count
                )
            )
        return result_schemas


    def mark_messages_as_read(self, db: Session, conversation_id: str, recipient_id: int) -> int:
        """Marks all messages in a conversation as read for the recipient. Returns count of updated messages."""
        updated_count = (
            db.query(MessageModel)
            .filter(
                MessageModel.conversation_id == conversation_id,
                MessageModel.recipient_id == recipient_id,
                MessageModel.is_read_by_recipient == False,
            )
            .update({"is_read_by_recipient": True}, synchronize_session=False)
        )
        db.commit()
        return updated_count

message_service = MessageService()
