from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.dependencies import get_current_active_user
from ..models.user import User as UserModel # For current_user type hint
from ..models.crop import Crop as CropModel
from ..schemas.crop import CropSchema, CropCreate, CropUpdate, ProfitCalculationResult
from ..services import crop_service # crop_service instance

router = APIRouter(
    prefix="/crops",
    tags=["Crops & Profitability"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=CropSchema, status_code=status.HTTP_201_CREATED)
async def create_new_crop_entry(
    crop_in: CropCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new crop entry with cost and yield details for the logged-in user."""
    return crop_service.create_crop(db=db, crop_in=crop_in, user_id=current_user.id)

@router.get("/", response_model=List[CropSchema])
async def get_user_crop_entries(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = Query(default=10, le=100)
):
    """Get all crop entries created by the currently logged-in user."""
    return crop_service.get_crops_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{crop_id}", response_model=CropSchema)
async def get_crop_entry_by_id(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get details of a specific crop entry. User must be the owner."""
    db_crop = crop_service.get_crop_by_id(db, crop_id=crop_id)
    if not db_crop:
        raise HTTPException(status_code=404, detail="Crop entry not found")
    if db_crop.user_id != current_user.id:
        # Add RBAC for admin if needed: and current_user.role != UserRole.ADMIN
        raise HTTPException(status_code=403, detail="Not authorized to access this crop entry")
    return db_crop

@router.put("/{crop_id}", response_model=CropSchema)
async def update_existing_crop_entry(
    crop_id: int,
    crop_in: CropUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update an existing crop entry. User must be the owner."""
    db_crop = crop_service.get_crop_by_id(db, crop_id=crop_id)
    if not db_crop:
        raise HTTPException(status_code=404, detail="Crop entry not found")
    if db_crop.user_id != current_user.id:
        # Add RBAC for admin if needed
        raise HTTPException(status_code=403, detail="Not authorized to update this crop entry")
    return crop_service.update_crop(db=db, db_crop=db_crop, crop_in=crop_in)

@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_crop_entry(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete an existing crop entry. User must be the owner."""
    db_crop = crop_service.get_crop_by_id(db, crop_id=crop_id)
    if not db_crop:
        raise HTTPException(status_code=404, detail="Crop entry not found")
    if db_crop.user_id != current_user.id:
        # Add RBAC for admin if needed
        raise HTTPException(status_code=403, detail="Not authorized to delete this crop entry")
    crop_service.delete_crop(db=db, crop_id=crop_id)
    return

@router.get("/{crop_id}/profit", response_model=ProfitCalculationResult)
async def get_crop_profitability_analysis(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Calculate and return the profitability analysis for a specific crop entry. User must be the owner."""
    db_crop = crop_service.get_crop_by_id(db, crop_id=crop_id)
    if not db_crop:
        raise HTTPException(status_code=404, detail="Crop entry not found")
    if db_crop.user_id != current_user.id:
        # Add RBAC for admin if needed
        raise HTTPException(status_code=403, detail="Not authorized to analyze this crop entry")
    return crop_service.calculate_profitability(crop=db_crop)
