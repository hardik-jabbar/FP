from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.service_booking import ServiceBooking as ServiceBookingModel, ServiceStatus
from ..models.user import UserRole # For role checks if needed
from ..schemas.service_booking import ServiceBookingCreate, ServiceBookingUpdate

class ServiceBookingService:
    def get_booking_by_id(self, db: Session, booking_id: int) -> Optional[ServiceBookingModel]:
        return db.query(ServiceBookingModel).filter(ServiceBookingModel.id == booking_id).first()

    def get_bookings_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ServiceBookingModel]:
        """Get bookings made by a specific user (customer)."""
        return db.query(ServiceBookingModel).filter(ServiceBookingModel.user_id == user_id).order_by(ServiceBookingModel.scheduled_date.desc()).offset(skip).limit(limit).all()

    def get_bookings_by_provider(self, db: Session, provider_id: int, skip: int = 0, limit: int = 100) -> List[ServiceBookingModel]:
        """Get bookings assigned to a specific service provider."""
        return db.query(ServiceBookingModel).filter(ServiceBookingModel.service_provider_id == provider_id).order_by(ServiceBookingModel.scheduled_date.desc()).offset(skip).limit(limit).all()

    def get_bookings_by_tractor(self, db: Session, tractor_id: int, skip: int = 0, limit: int = 100) -> List[ServiceBookingModel]:
        """Get bookings associated with a specific tractor."""
        return db.query(ServiceBookingModel).filter(ServiceBookingModel.tractor_id == tractor_id).order_by(ServiceBookingModel.scheduled_date.desc()).offset(skip).limit(limit).all()

    def get_all_bookings(self, db: Session, skip: int = 0, limit: int = 100) -> List[ServiceBookingModel]:
        """Get all bookings (typically for admin use)."""
        return db.query(ServiceBookingModel).order_by(ServiceBookingModel.scheduled_date.desc()).offset(skip).limit(limit).all()

    def create_booking(self, db: Session, booking_in: ServiceBookingCreate, user_id: int) -> ServiceBookingModel:
        booking_data = booking_in.model_dump()
        # Status is defaulted in the model to PENDING, or can be set here if needed.
        db_booking = ServiceBookingModel(**booking_data, user_id=user_id, status=ServiceStatus.PENDING)
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking

    def update_booking(self, db: Session, db_booking: ServiceBookingModel, booking_in: ServiceBookingUpdate) -> ServiceBookingModel:
        update_data = booking_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_booking, field, value)
        db.add(db_booking) # Mark as dirty
        db.commit()
        db.refresh(db_booking)
        return db_booking

    def update_booking_status(self, db: Session, db_booking: ServiceBookingModel, status: ServiceStatus) -> ServiceBookingModel:
        db_booking.status = status
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking

    def delete_booking(self, db: Session, booking_id: int) -> Optional[ServiceBookingModel]:
        db_booking = self.get_booking_by_id(db, booking_id)
        if db_booking:
            db.delete(db_booking) # Or mark as CANCELLED if soft delete is preferred
            db.commit()
        return db_booking

service_booking_service = ServiceBookingService() # Instantiate the service
