from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.dependencies import get_current_active_user
from ..models.user import User as UserModel, UserRole
from ..models.service_booking import ServiceStatus # For status updates
from ..schemas.service_booking import ServiceBookingSchema, ServiceBookingCreate, ServiceBookingUpdate
from ..services import service_booking_service # Import the service_booking_service instance

router = APIRouter(
    prefix="/service-bookings", # Changed prefix to be more RESTful
    tags=["Service Bookings"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ServiceBookingSchema, status_code=status.HTTP_201_CREATED)
async def create_new_service_booking(
    booking_in: ServiceBookingCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a new service booking. The booking user_id is automatically set to the current authenticated user.
    """
    # Additional validation: e.g., check if tractor_id exists and belongs to user if provided
    # Check if service_provider_id is a valid provider if provided
    return service_booking_service.create_booking(db=db, booking_in=booking_in, user_id=current_user.id)

@router.get("/", response_model=List[ServiceBookingSchema])
async def get_service_bookings_list(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    view_as_provider: bool = Query(False, description="Set to true if service provider is viewing their assigned bookings")
):
    """
    Get a list of service bookings.
    - Regular users see their own bookings.
    - Service Providers see bookings assigned to them if view_as_provider is true.
    - Admins see all bookings.
    """
    if current_user.role == UserRole.ADMIN:
        return service_booking_service.get_all_bookings(db=db, skip=skip, limit=limit)
    elif current_user.role == UserRole.SERVICE_PROVIDER and view_as_provider:
        return service_booking_service.get_bookings_by_provider(db=db, provider_id=current_user.id, skip=skip, limit=limit)
    else: # Default for FARMER, DEALER, or SERVICE_PROVIDER not viewing as provider
        return service_booking_service.get_bookings_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{booking_id}", response_model=ServiceBookingSchema)
async def get_specific_service_booking_details(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get details of a specific service booking.
    Accessible by the customer, assigned service provider, or an ADMIN.
    """
    booking = service_booking_service.get_booking_by_id(db, booking_id=booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service booking not found")

    is_customer = booking.user_id == current_user.id
    is_assigned_provider = booking.service_provider_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_customer or is_assigned_provider or is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this service booking")
    return booking

@router.put("/{booking_id}", response_model=ServiceBookingSchema)
async def update_service_booking_details(
    booking_id: int,
    booking_in: ServiceBookingUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update details of a service booking.
    - Customer can update if status is PENDING.
    - Assigned Service Provider can update status or add notes.
    - Admin can update any booking.
    """
    db_booking = service_booking_service.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service booking not found")

    is_customer = db_booking.user_id == current_user.id
    is_assigned_provider = db_booking.service_provider_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_admin or (is_customer and db_booking.status == ServiceStatus.PENDING) or is_assigned_provider):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this service booking or booking is not in a modifiable state")

    # Further logic can be added in the service layer to restrict what fields each role can update
    # e.g. customer can only change description/notes if PENDING, provider can only change status/provider_notes
    return service_booking_service.update_booking(db=db, db_booking=db_booking, booking_in=booking_in)

@router.patch("/{booking_id}/status", response_model=ServiceBookingSchema)
async def update_service_booking_status_endpoint(
    booking_id: int,
    status_in: ServiceStatus, # Directly pass the new status
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update the status of a specific service booking.
    Accessible by assigned service provider or ADMIN. Customer might only cancel.
    """
    db_booking = service_booking_service.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    is_assigned_provider = db_booking.service_provider_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN
    is_customer_cancelling = (db_booking.user_id == current_user.id and
                              status_in == ServiceStatus.CANCELLED_BY_USER and
                              db_booking.status in [ServiceStatus.PENDING, ServiceStatus.CONFIRMED])


    if not (is_admin or is_assigned_provider or is_customer_cancelling):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update status for this booking or invalid status transition")

    # Add more complex status transition logic in the service if needed
    return service_booking_service.update_booking_status(db=db, db_booking=db_booking, status=status_in)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_or_delete_service_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Cancel or delete a service booking.
    Customer can cancel PENDING/CONFIRMED bookings (moves to CANCELLED_BY_USER).
    Admin can delete any booking.
    """
    db_booking = service_booking_service.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service booking not found")

    is_customer = db_booking.user_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if is_admin:
        service_booking_service.delete_booking(db=db, booking_id=booking_id)
    elif is_customer and db_booking.status in [ServiceStatus.PENDING, ServiceStatus.CONFIRMED]:
        service_booking_service.update_booking_status(db=db, db_booking=db_booking, status=ServiceStatus.CANCELLED_BY_USER)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel or delete this booking, or booking is not in a cancellable state.")
    return

@router.get("/availability/", include_in_schema=False) # include_in_schema=False for now
async def get_service_provider_availability():
    """
    Placeholder for fetching service provider availability.
    This would typically involve more complex logic, possibly checking calendars or schedules.
    """
    # In a real app, this might query a different model or external service.
    return {"message": "Technician availability feature not yet fully implemented. Please check back later or contact support."}
