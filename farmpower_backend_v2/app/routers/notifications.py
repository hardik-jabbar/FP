from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.dependencies import get_current_active_user, RoleChecker # RoleChecker for admin-only create
from ..models.user import User as UserModel, UserRole
from ..schemas.notification import NotificationSchema, NotificationCreateInternal # For admin/internal creation
from ..services import notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
    responses={404: {"description": "Not found"}},
)

# This endpoint is for internal/admin use to create notifications for any user.
# For user-triggered notifications (e.g. new message), the logic would be within those specific services/routers.
@router.post("/", response_model=NotificationSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RoleChecker([UserRole.ADMIN]))]) # Example: Admin only
async def create_notification_for_user(
    notification_in: NotificationCreateInternal, # Requires user_id to be specified
    db: Session = Depends(get_db)
):
    """
    Create a new notification for a specific user. (Admin/System use)
    """
    # TODO: Validate if user_id in notification_in exists if necessary, or trust internal use.
    return notification_service.create_notification(db=db, notification_in=notification_in)

@router.get("/", response_model=List[NotificationSchema])
async def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    unread_only: Optional[bool] = Query(False, description="Set to true to fetch only unread notifications")
):
    """
    Get notifications for the currently authenticated user. Supports pagination and filtering by unread status.
    """
    return notification_service.get_notifications_for_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit, unread_only=unread_only
    )

@router.patch("/{notification_id}/read", response_model=NotificationSchema)
async def mark_one_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Mark a specific notification as read for the current user.
    """
    updated_notification = notification_service.mark_notification_as_read(
        db=db, notification_id=notification_id, user_id=current_user.id
    )
    if not updated_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or you're not authorized to modify it."
        )
    return updated_notification

@router.post("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_my_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Mark all unread notifications as read for the current user.
    Returns the count of notifications that were marked as read.
    """
    updated_count = notification_service.mark_all_notifications_as_read(db=db, user_id=current_user.id)
    return {"message": f"{updated_count} notifications marked as read."}
