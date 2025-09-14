from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.equipment import Equipment, Booking, MaintenanceRecord
from app.schemas.equipment import EquipmentCreate, EquipmentFilter, BookingCreate, MaintenanceRecordCreate

def create_equipment(db: Session, equipment: EquipmentCreate, owner_id: int) -> Equipment:
    db_equipment = Equipment(
        **equipment.dict(),
        owner_id=owner_id,
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def get_equipment(db: Session, equipment_id: int) -> Optional[Equipment]:
    return db.query(Equipment).filter(Equipment.id == equipment_id).first()

def get_equipment_list(
    db: Session,
    filter_params: EquipmentFilter,
    skip: int = 0,
    limit: int = 10
) -> List[Equipment]:
    query = db.query(Equipment)

    if filter_params.type:
        query = query.filter(Equipment.type == filter_params.type)
    if filter_params.manufacturer:
        query = query.filter(Equipment.manufacturer == filter_params.manufacturer)
    if filter_params.min_price:
        query = query.filter(Equipment.price_per_day >= filter_params.min_price)
    if filter_params.max_price:
        query = query.filter(Equipment.price_per_day <= filter_params.max_price)
    if filter_params.location:
        query = query.filter(Equipment.location == filter_params.location)
    
    # Handle availability filtering
    if filter_params.available_from and filter_params.available_to:
        query = query.filter(~Equipment.bookings.any(
            (Booking.start_date <= filter_params.available_to) &
            (Booking.end_date >= filter_params.available_from)
        ))

    return query.offset(skip).limit(limit).all()

def update_equipment(db: Session, equipment_id: int, equipment_data: EquipmentCreate) -> Equipment:
    db_equipment = get_equipment(db, equipment_id)
    for key, value in equipment_data.dict().items():
        setattr(db_equipment, key, value)
    db_equipment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def delete_equipment(db: Session, equipment_id: int) -> None:
    db_equipment = get_equipment(db, equipment_id)
    db.delete(db_equipment)
    db.commit()

def create_booking(db: Session, booking: BookingCreate, user_id: int) -> Booking:
    # Calculate total price based on equipment price and booking duration
    equipment = get_equipment(db, booking.equipment_id)
    days = (booking.end_date - booking.start_date).days
    total_price = equipment.price_per_day * days

    db_booking = Booking(
        **booking.dict(),
        user_id=user_id,
        total_price=total_price,
        status="pending",
        payment_status="unpaid",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_equipment_bookings(db: Session, equipment_id: int) -> List[Booking]:
    return db.query(Booking).filter(Booking.equipment_id == equipment_id).all()

def create_maintenance_record(db: Session, maintenance: MaintenanceRecordCreate) -> MaintenanceRecord:
    db_maintenance = MaintenanceRecord(
        **maintenance.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance