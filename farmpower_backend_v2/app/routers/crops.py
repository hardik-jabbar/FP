from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.dependencies import get_current_active_user
from ..models.user import User as UserModel, UserRole # For auth and role checks if needed
# CropModel not directly used here as service handles DB interaction
from ..schemas.crop import CropSchema, CropCreate, CropUpdate, ProfitCalculationResult
from ..services import crop_service # Import the crop_service instance

router = APIRouter(
    prefix="/crops",
    tags=["Crops & Profitability"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=CropSchema, status_code=status.HTTP_201_CREATED)
async def create_new_crop_profitability_entry(
    crop_in: CropCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a new crop entry with associated costs and yield projections
    for profitability analysis.
    """
    # user_id is automatically taken from the authenticated user.
    return crop_service.create_crop(db=db, crop_in=crop_in, user_id=current_user.id)

@router.get("/", response_model=List[CropSchema])
async def get_user_created_crop_entries(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all crop entries created by the currently authenticated user.
    Supports pagination.
    """
    return crop_service.get_crops_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{crop_id}", response_model=CropSchema)
async def get_specific_crop_entry_details(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get details of a specific crop entry.
    The user must be the owner of the crop entry or an ADMIN.
    """
    db_crop = crop_service.get_crop_by_id(db, crop_id=crop_id)
    if not db_crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop entry not found")
    if db_crop.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this crop entry")
    return db_crop

@router.put("/{crop_id}", response_model=CropSchema)
async def update_crop_entry_details(
    crop_id: int,
    crop_in: CropUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update an existing crop entry.
    The user must be the owner of the crop entry or an ADMIN.
    """
    db_crop = crop_service.get_crop_by_id(db, crop_id=crop_id)
    if not db_crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop entry not found")
    if db_crop.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this crop entry")
    return crop_service.update_crop(db=db, db_crop=db_crop, crop_in=crop_in)

@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crop_entry_permanently(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Delete an existing crop entry permanently.
    The user must be the owner of the crop entry or an ADMIN.
    """
    db_crop = crop_service.get_crop_by_id(db, crop_id=crop_id)
    if not db_crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop entry not found")
    if db_crop.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this crop entry")

    deleted_crop = crop_service.delete_crop(db=db, crop_id=crop_id)
    if not deleted_crop: # Should ideally not happen if previous checks passed
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop entry not found during delete operation")
    return

@router.get("/{crop_id}/profit", response_model=ProfitCalculationResult)
async def get_profitability_analysis_for_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Calculate and return the profitability analysis for a specific crop entry.
    The user must be the owner of the crop entry or an ADMIN.
    """
    db_crop = crop_service.get_crop_by_id(db, crop_id=crop_id)
    if not db_crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop entry not found")
    if db_crop.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to analyze this crop entry")
    return crop_service.calculate_profitability(crop=db_crop)
