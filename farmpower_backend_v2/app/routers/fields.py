from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.dependencies import get_current_active_user # Assuming RoleChecker might be used for specific admin actions
from ..models.user import User as UserModel, UserRole # UserRole for admin checks
# FieldModel and LandUsagePlanModel are not directly used here as service handles DB interaction
from ..schemas.field import FieldSchema, FieldCreate, FieldUpdate
from ..schemas.land_usage_plan import LandUsagePlanSchema, LandUsagePlanCreate, LandUsagePlanUpdate
from ..services import field_service # Import the field_service instance

router = APIRouter(
    prefix="/fields",
    tags=["Fields & Land Usage Plans"],
    responses={404: {"description": "Not found"}},
)

# --- Field Endpoints ---

@router.post("/", response_model=FieldSchema, status_code=status.HTTP_201_CREATED)
async def create_new_user_field(
    field_in: FieldCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new field entry for the currently authenticated user."""
    # owner_id is taken from current_user.id
    return field_service.create_field(db=db, field_in=field_in, owner_id=current_user.id)

@router.get("/", response_model=List[FieldSchema])
async def get_current_user_fields(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get all fields registered by the currently authenticated user."""
    return field_service.get_fields_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)

@router.get("/{field_id}", response_model=FieldSchema)
async def get_specific_field_details(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get details of a specific field. User must own the field or be an ADMIN."""
    db_field = field_service.get_field_by_id(db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    if db_field.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this field")
    return db_field

@router.put("/{field_id}", response_model=FieldSchema)
async def update_user_field_details(
    field_id: int,
    field_in: FieldUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update an existing field. User must be the owner or an ADMIN."""
    db_field = field_service.get_field_by_id(db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    if db_field.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this field")
    return field_service.update_field(db=db, db_field=db_field, field_in=field_in)

@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_field(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete an existing field. User must be the owner or an ADMIN."""
    db_field = field_service.get_field_by_id(db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    if db_field.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this field")

    deleted_field = field_service.delete_field(db=db, field_id=field_id)
    if not deleted_field: # Should not happen if previous check passed
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found during delete operation")
    return

# --- Land Usage Plan Endpoints (Nested under Fields) ---

@router.post("/{field_id}/plans/", response_model=LandUsagePlanSchema, status_code=status.HTTP_201_CREATED)
async def create_plan_for_field(
    field_id: int,
    plan_in: LandUsagePlanCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new land usage plan for a specific field owned by the user (or if admin)."""
    db_field = field_service.get_field_by_id(db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    if db_field.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add plans to this field")
    return field_service.create_land_usage_plan(db=db, plan_in=plan_in, field_id=field_id)

@router.get("/{field_id}/plans/", response_model=List[LandUsagePlanSchema])
async def list_plans_for_field(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get all land usage plans for a specific field. User must own field or be ADMIN."""
    db_field = field_service.get_field_by_id(db, field_id=field_id)
    if not db_field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    if db_field.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view plans for this field")
    return field_service.get_plans_for_field(db=db, field_id=field_id, skip=skip, limit=limit)

# Standalone plan management might be useful too, but requires careful auth.
# These are accessed via /fields/plans/{plan_id}
@router.get("/plans/{plan_id}", response_model=LandUsagePlanSchema)
async def get_specific_land_usage_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get details of a specific land usage plan. User must own parent field or be ADMIN."""
    db_plan = field_service.get_plan_by_id(db, plan_id=plan_id)
    if not db_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Land usage plan not found")

    # Verify ownership through the parent field
    db_field = field_service.get_field_by_id(db, field_id=db_plan.field_id)
    if not db_field or (db_field.owner_id != current_user.id and current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this plan")
    return db_plan

@router.put("/plans/{plan_id}", response_model=LandUsagePlanSchema)
async def update_specific_land_usage_plan(
    plan_id: int,
    plan_in: LandUsagePlanUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update an existing land usage plan. User must own parent field or be ADMIN."""
    db_plan = field_service.get_plan_by_id(db, plan_id=plan_id)
    if not db_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    db_field = field_service.get_field_by_id(db, field_id=db_plan.field_id)
    if not db_field or (db_field.owner_id != current_user.id and current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this plan")

    return field_service.update_land_usage_plan(db=db, db_plan=db_plan, plan_in=plan_in)

@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specific_land_usage_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete an existing land usage plan. User must own parent field or be ADMIN."""
    db_plan = field_service.get_plan_by_id(db, plan_id=plan_id)
    if not db_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    db_field = field_service.get_field_by_id(db, field_id=db_plan.field_id)
    if not db_field or (db_field.owner_id != current_user.id and current_user.role != UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this plan")

    deleted_plan = field_service.delete_land_usage_plan(db=db, plan_id=plan_id)
    if not deleted_plan: # Should not happen if previous check passed
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found during delete operation")
    return
