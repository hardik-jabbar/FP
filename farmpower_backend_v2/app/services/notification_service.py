from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.notification import Notification as NotificationModel, NotificationType
from ..schemas.notification import NotificationCreateInternal # For creating notifications

class NotificationService:
    def get_notification_by_id(self, db: Session, notification_id: int) -> Optional[NotificationModel]:
        return db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()

    def get_notifications_for_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20, # Default to 20 notifications per page
        unread_only: Optional[bool] = False
    ) -> List[NotificationModel]:
        query = db.query(NotificationModel).filter(NotificationModel.user_id == user_id)
        if unread_only:
            query = query.filter(NotificationModel.is_read == False)
        return query.order_by(NotificationModel.created_at.desc()).offset(skip).limit(limit).all()

    def create_notification(self, db: Session, notification_in: NotificationCreateInternal) -> NotificationModel:
        """
        Creates a notification for a user.
        `notification_in` should be `NotificationCreateInternal` schema with `user_id`.
        """
        db_notification = NotificationModel(
            user_id=notification_in.user_id,
            title=notification_in.title,
            message=notification_in.message,
            type=notification_in.type,
            related_entity_type=notification_in.related_entity_type,
            related_entity_id=notification_in.related_entity_id
            # is_read defaults to False in the model
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        # TODO: Here you might trigger a real-time push notification (e.g., via WebSockets or Firebase)
        # await sio.emit('new_notification', {'notification_id': db_notification.id, 'title': db_notification.title}, room=f'user_{db_notification.user_id}')
        return db_notification

    def mark_notification_as_read(self, db: Session, notification_id: int, user_id: int) -> Optional[NotificationModel]:
        """Marks a specific notification as read for a user if they are the recipient."""
        db_notification = self.get_notification_by_id(db, notification_id)
        if db_notification and db_notification.user_id == user_id:
            if not db_notification.is_read:
                db_notification.is_read = True
                db.add(db_notification)
                db.commit()
                db.refresh(db_notification)
            return db_notification
        return None

    def mark_all_notifications_as_read(self, db: Session, user_id: int) -> int:
        """Marks all unread notifications for a user as read. Returns count of updated notifications."""
        updated_count = db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == False
        ).update({"is_read": True}, synchronize_session=False) # 'fetch' might be better for some dbs
        db.commit()
        return updated_count

notification_service = NotificationService()
