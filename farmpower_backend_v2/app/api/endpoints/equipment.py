from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.crud import equipment as equipment_crud
from app.schemas.equipment import (
    Equipment, EquipmentCreate, EquipmentFilter,
    Booking, BookingCreate,
    MaintenanceRecord, MaintenanceRecordCreate
)
from app.core.deps import get_db, get_current_user
from app.models.user import User as DBUser

router = APIRouter(prefix="/api/equipment", tags=["equipment"])

@router.post("/", response_model=Equipment)
def create_equipment(
    equipment: EquipmentCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new equipment listing"""
    return equipment_crud.create_equipment(db, equipment, current_user.id)

@router.get("/", response_model=List[Equipment])
def list_equipment(
    filter_params: EquipmentFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all equipment with optional filtering"""
    return equipment_crud.get_equipment_list(db, filter_params, skip, limit)

@router.get("/{equipment_id}", response_model=Equipment)
def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """Get details of a specific equipment"""
    equipment = equipment_crud.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.put("/{equipment_id}", response_model=Equipment)
def update_equipment(
    equipment_id: int,
    equipment_data: EquipmentCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update equipment details"""
    equipment = equipment_crud.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this equipment")
    return equipment_crud.update_equipment(db, equipment_id, equipment_data)

@router.delete("/{equipment_id}")
def delete_equipment(
    equipment_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an equipment listing"""
    equipment = equipment_crud.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this equipment")
    equipment_crud.delete_equipment(db, equipment_id)
    return {"message": "Equipment deleted successfully"}

@router.post("/{equipment_id}/bookings", response_model=Booking)
def create_booking(
    equipment_id: int,
    booking: BookingCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new booking for equipment"""
    equipment = equipment_crud.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if not equipment.is_available:
        raise HTTPException(status_code=400, detail="Equipment is not available for booking")
    return equipment_crud.create_booking(db, booking, current_user.id)

@router.get("/{equipment_id}/bookings", response_model=List[Booking])
def list_equipment_bookings(
    equipment_id: int,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all bookings for a specific equipment"""
    equipment = equipment_crud.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view bookings")
    return equipment_crud.get_equipment_bookings(db, equipment_id)

@router.post("/{equipment_id}/maintenance", response_model=MaintenanceRecord)
def create_maintenance_record(
    equipment_id: int,
    maintenance: MaintenanceRecordCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a maintenance record for equipment"""
    equipment = equipment_crud.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add maintenance records")
    return equipment_crud.create_maintenance_record(db, maintenance)