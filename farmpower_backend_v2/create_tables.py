from app.core.db import Base, engine, SessionLocal
from app.models import (
    user, tractor, field, crop, land_usage_plan,
    message, notification, part, service_booking,
    crop_calculator
)
from app.core.config import settings
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.models.user import UserRole
from datetime import datetime, timedelta
import json

# Import all necessary schemas for seeding
from app.schemas.tractor import TractorCreate
from app.schemas.field import FieldCreate
from app.schemas.crop import CropCreate
from app.schemas.part import PartCreate
from app.schemas.service_booking import ServiceBookingCreate
from app.schemas.notification import NotificationCreateInternal
from app.schemas.message import MessageCreate

def create_tables():
    """Create all database tables."""
    print(f"Attempting to create tables. Discovered tables: {list(Base.metadata.tables.keys())}")
    Base.metadata.drop_all(bind=engine) # Drop existing tables
    Base.metadata.create_all(bind=engine)

def seed_initial_data(db: Session):
    """Seed initial data for testing."""
    user_service = UserService()

    # Create admin user
    admin_user = UserCreate(
        email="admin@farmpower.com",
        password="admin123",
        full_name="Admin User",
        role=UserRole.ADMIN
    )
    admin = user_service.create_user(db, admin_user)

    # Create dealer user
    dealer_user = UserCreate(
        email="dealer@farmpower.com",
        password="dealer123",
        full_name="Dealer User",
        role=UserRole.DEALER
    )
    dealer = user_service.create_user(db, dealer_user)

    # Create service provider
    service_provider = UserCreate(
        email="service@farmpower.com",
        password="service123",
        full_name="Service Provider",
        role=UserRole.SERVICE_PROVIDER
    )
    provider = user_service.create_user(db, service_provider)

    # Create farmer
    farmer_user = UserCreate(
        email="farmer@farmpower.com",
        password="farmer123",
        full_name="Farmer User",
        role=UserRole.FARMER
    )
    farmer = user_service.create_user(db, farmer_user)

    # Create a sample tractor
    from app.services.tractor_service import TractorService
    tractor_service = TractorService()
    
    tractor_data = TractorCreate(
        name="John Deere 5055E",
        brand="John Deere",
        model="5055E",
        year=2020,
        price=25000.00,
        location="New York",
        description="Well maintained tractor with low hours",
        horsepower=55,
        condition="Used - Good",
        image_urls=[]
    )
    tractor = tractor_service.create_tractor(db, tractor_data, dealer.id)

    # Create a sample field
    from app.services.field_service import FieldService
    field_service = FieldService()
    
    field_data = FieldCreate(
        name="North Field",
        coordinates={
            "type": "Polygon",
            "coordinates": [[
                [100.0, 0.0],
                [101.0, 0.0],
                [101.0, 1.0],
                [100.0, 1.0],
                [100.0, 0.0]
            ]]
        },
        area_hectares=12.5,
        crop_info="Currently planted with Corn",
        soil_type="Loam"
    )
    field = field_service.create_field(db, field_data, farmer.id)

    # Create a sample crop
    from app.services.crop_service import CropService
    crop_service = CropService()
    
    crop_data = CropCreate(
        name="Corn",
        crop_variety="Yellow Dent #2",
        seed_cost_per_hectare=120.50,
        fertilizer_cost_per_hectare=180.75,
        pesticide_cost_per_hectare=60.0,
        machinery_cost_per_hectare=75.25,
        labor_cost_per_hectare=90.0,
        other_costs_per_hectare=30.50,
        expected_yield_per_hectare=12.0,
        yield_unit="tonnes",
        market_price_per_unit=190.0,
        notes="Standard planting for this region",
        field_id=field.id
    )
    crop = crop_service.create_crop(db, crop_data, farmer.id)

    # Create a sample part
    from app.services.part_service import PartService
    part_service = PartService()
    
    part_data = PartCreate(
        name="Oil Filter",
        category="Filters",
        brand="Fleetguard",
        part_number="LF9001",
        price=25.99,
        location="New York",
        description="High-quality oil filter for John Deere tractors",
        condition="New",
        image_urls=[],
        tractor_brand_compatibility=["John Deere"],
        tractor_model_compatibility=["John Deere 5055E"],
        quantity=10
    )
    part = part_service.create_part(db, part_data, dealer.id)

    # Create a sample service booking
    from app.services.service_booking_service import ServiceBookingService
    service_booking_service = ServiceBookingService()
    
    booking_data = ServiceBookingCreate(
        tractor_id=tractor.id,
        service_type="Regular Maintenance",
        description="600-hour service required",
        scheduled_date=datetime.utcnow() + timedelta(days=7),
        service_provider_id=provider.id,
        notes="Please check all fluid levels"
    )
    booking = service_booking_service.create_booking(db, booking_data, farmer.id)

    # Create a sample notification
    from app.services.notification_service import NotificationService
    notification_service = NotificationService()
    
    notification_data = NotificationCreateInternal(
        user_id=farmer.id,
        title="Service Reminder",
        message="Your tractor service is scheduled for next week",
        type="service_reminder",
        related_entity_type="service_booking",
        related_entity_id=booking.id
    )
    notification = notification_service.create_notification(db, notification_data)

    # Create a sample message
    from app.services.message_service import MessageService
    message_service = MessageService()
    
    message_data = MessageCreate(
        recipient_id=dealer.id,
        content="Is this tractor still available?"
    )
    message = message_service.create_message(db, message_data, farmer.id)

    print("Initial data seeded successfully!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_tables()
        seed_initial_data(db)
    finally:
        db.close() 