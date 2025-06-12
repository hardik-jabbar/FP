from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.dependencies import get_current_active_user, RoleChecker # RoleChecker for admin-only routes
from ..models.user import User as UserModel, UserRole
from ..schemas.user import UserSchema # For returning user details
from ..schemas.tractor import TractorSchema # For returning tractor listings
from ..schemas.part import PartSchema # For returning part listings
from ..services import user_service, tractor_service, part_service, admin_service # Import all relevant services

router = APIRouter(
    prefix="/admin",
    tags=["Admin Panel"],
    dependencies=[Depends(RoleChecker([UserRole.ADMIN]))], # Secure all routes in this router
    responses={
        403: {"description": "Operation not permitted or insufficient privileges"},
        404: {"description": "Resource not found"}
    },
)

# --- User Management by Admin ---

@router.get("/users/", response_model=List[UserSchema])
async def admin_list_all_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500) # Admin might need larger limits
):
    """
    [ADMIN ONLY] Get a list of all users in the system. Supports pagination.
    """
    users = user_service.get_all_users(db, skip=skip, limit=limit)
    return users

@router.post("/users/{user_id}/ban", response_model=UserSchema)
async def admin_ban_user_account(user_id: int, db: Session = Depends(get_db)):
    """
    [ADMIN ONLY] Ban a user account. This sets `is_banned=True` and `is_active=False`.
    """
    user_to_ban = user_service.get_user_by_id(db, user_id=user_id)
    if not user_to_ban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user_to_ban.role == UserRole.ADMIN: # Prevent banning other admins for safety
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot ban an admin user.")

    banned_user = admin_service.ban_user(db, user_id=user_id)
    if not banned_user: # Should be caught by get_user_by_id, but defensive
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or could not be banned.")
    return banned_user

@router.post("/users/{user_id}/unban", response_model=UserSchema)
async def admin_unban_user_account(user_id: int, db: Session = Depends(get_db)):
    """
    [ADMIN ONLY] Unban a user account. This sets `is_banned=False`.
    Does not automatically re-activate the account.
    """
    user_to_unban = user_service.get_user_by_id(db, user_id=user_id)
    if not user_to_unban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    unbanned_user = admin_service.unban_user(db, user_id=user_id)
    if not unbanned_user: # Should be caught by get_user_by_id
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or could not be unbanned.")
    return unbanned_user

# --- Listings Management by Admin ---

@router.get("/tractors/", response_model=List[TractorSchema])
async def admin_list_all_tractors(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    # Add other filters from tractor_service.get_tractors if needed by admin
    brand: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    owner_id: Optional[int] = Query(None, description="Filter by original owner ID")
):
    """
    [ADMIN ONLY] Get a list of all tractor listings in the system.
    """
    # The `owner_id` filter is passed directly. Other filters can be added.
    # The `tractor_service.get_tractors` can be used directly.
    # If it needs an 'admin_mode' flag, that would be a service layer change.
    tractors = tractor_service.get_tractors(db, skip=skip, limit=limit, brand=brand, location=location, owner_id=owner_id)
    return tractors

@router.get("/parts/", response_model=List[PartSchema])
async def admin_list_all_parts(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    # Add other filters from part_service.get_parts if needed
    category: Optional[str] = Query(None),
    seller_id: Optional[int] = Query(None, description="Filter by original seller ID")
):
    """
    [ADMIN ONLY] Get a list of all part listings in the system.
    """
    parts = part_service.get_parts(db, skip=skip, limit=limit, category=category, seller_id=seller_id)
    return parts

# TODO: Admin endpoints for deleting/suspending specific tractor/part listings if different from user actions

# --- Site Analytics ---
@router.get("/statistics/", response_model=Dict[str, Any])
async def admin_get_site_statistics(db: Session = Depends(get_db)):
    """
    [ADMIN ONLY] Get basic site statistics (e.g., counts of users, listings).
    """
    return admin_service.get_site_statistics(db)
