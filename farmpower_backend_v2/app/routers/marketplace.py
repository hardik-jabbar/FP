from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas.tractor import TractorSchema, TractorCreate, TractorUpdate
from ..schemas.part import PartSchema, PartCreate, PartUpdate
from ..core.dependencies import get_current_user
from ..services.tractor_service import tractor_service
from ..services.part_service import part_service
from ..models.user import User as UserModel # Import User model for type hinting current_user

router = APIRouter(
    prefix="/marketplace",
    tags=["marketplace"]
)

# Dummy data moved to a more appropriate place or seeded via service if needed

@router.post("/seed-dummy-data", status_code=status.HTTP_200_OK)
def seed_dummy_data(db: Session = Depends(get_db)):
    """Endpoint to seed dummy data for testing"""
    try:
        # Example dummy data for seeding via services
        # These should ideally be part of a separate data seeding script, not an API endpoint
        # but for quick testing as requested, we'll keep it here temporarily.
        dummy_tractors = [
            {
                "name": "John Deere 8R 410",
                "brand": "John Deere",
                "model": "8R 410",
                "year": 2023,
                "price": 350000.00,
                "condition": "New",
                "description": "High-performance 4WD tractor with advanced technology",
                "horsepower": 410,
                "location": "Iowa, USA",
                "image_urls": []
            },
            {
                "name": "Case IH Steiger 620",
                "brand": "Case IH",
                "model": "Steiger 620",
                "year": 2022,
                "price": 425000.00,
                "condition": "Like New",
                "description": "Powerful articulated tractor for large-scale farming",
                "horsepower": 620,
                "location": "Illinois, USA",
                "image_urls": []
            }
        ]

        dummy_parts = [
            {
                "name": "Tractor Engine Filter",
                "category": "Filters",
                "brand": "John Deere",
                "price": 45.99,
                "description": "High-quality engine air filter for John Deere tractors",
                "condition": "New",
                "quantity": 50,
                "location": "Warehouse A",
                "image_urls": []
            },
            {
                "name": "Hydraulic Pump",
                "category": "Hydraulics",
                "brand": "Case IH",
                "price": 1250.00,
                "description": "Replacement hydraulic pump for Case IH Steiger series",
                "condition": "Used - Good",
                "quantity": 10,
                "location": "Warehouse B",
                "image_urls": []
            }
        ]

        # Assuming a default user (id=1) for seeding. In a real app, this should be an admin user.
        # Need to ensure a user with ID 1 exists for these to work.
        # For testing, you might need to manually create a user first or adjust this logic.
        user_id_for_seeding = 1 

        for tractor_data in dummy_tractors:
            tractor_create = TractorCreate(**tractor_data)
            tractor_service.create_tractor(db, tractor_create, owner_id=user_id_for_seeding)
        
        for part_data in dummy_parts:
            part_create = PartCreate(**part_data)
            part_service.create_part(db, part_create, seller_id=user_id_for_seeding)
        
        return {"message": "Dummy data seeded successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Tractor endpoints
@router.get("/tractors", response_model=List[TractorSchema])
def get_tractors(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=200),
    brand: Optional[str] = Query(None, description="Filter by brand name (case-insensitive)"),
    location: Optional[str] = Query(None, description="Filter by location (case-insensitive)"),
    min_price: Optional[float] = Query(None, alias="minPrice", gt=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, alias="maxPrice", gt=0, description="Maximum price filter"),
    db: Session = Depends(get_db)
):
    tractors = tractor_service.get_tractors(db, skip=skip, limit=limit, brand=brand, location=location, min_price=min_price, max_price=max_price)
    return tractors

@router.get("/tractors/{tractor_id}", response_model=TractorSchema)
def get_tractor(tractor_id: int, db: Session = Depends(get_db)):
    tractor = tractor_service.get_tractor_by_id(db, tractor_id)
    if not tractor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tractor not found")
    return tractor

@router.post("/tractors", response_model=TractorSchema, status_code=status.HTTP_201_CREATED)
def create_tractor(
    tractor_in: TractorCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return tractor_service.create_tractor(db, tractor_in, owner_id=current_user.id)

@router.put("/tractors/{tractor_id}", response_model=TractorSchema)
def update_tractor(
    tractor_id: int,
    tractor_in: TractorUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id)
    if not db_tractor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tractor not found")
    if db_tractor.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this tractor")
    
    return tractor_service.update_tractor(db, db_tractor, tractor_in)

@router.delete("/tractors/{tractor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tractor(
    tractor_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id)
    if not db_tractor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tractor not found")
    if db_tractor.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this tractor")
    
    tractor_service.delete_tractor(db, tractor_id)
    return

# Part endpoints
@router.get("/parts", response_model=List[PartSchema])
def get_parts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=200),
    category: Optional[str] = Query(None, description="Filter by part category (case-insensitive)"),
    brand: Optional[str] = Query(None, description="Filter by brand name (case-insensitive)"),
    min_price: Optional[float] = Query(None, alias="minPrice", gt=0),
    max_price: Optional[float] = Query(None, alias="maxPrice", gt=0),
    location: Optional[str] = Query(None, description="Filter by seller's location for the part"),
    db: Session = Depends(get_db)
):
    parts = part_service.get_parts(db, skip=skip, limit=limit, category=category, brand=brand, min_price=min_price, max_price=max_price, location=location)
    return parts

@router.get("/parts/{part_id}", response_model=PartSchema)
def get_part(part_id: int, db: Session = Depends(get_db)):
    part = part_service.get_part_by_id(db, part_id)
    if not part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")
    return part

@router.post("/parts", response_model=PartSchema, status_code=status.HTTP_201_CREATED)
def create_part(
    part_in: PartCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return part_service.create_part(db, part_in, seller_id=current_user.id)

@router.put("/parts/{part_id}", response_model=PartSchema)
def update_part(
    part_id: int,
    part_in: PartUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_part = part_service.get_part_by_id(db, part_id)
    if not db_part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")
    if db_part.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this part")
    
    return part_service.update_part(db, db_part, part_in)

@router.delete("/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_part = part_service.get_part_by_id(db, part_id)
    if not db_part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")
    if db_part.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this part")
    
    part_service.delete_part(db, part_id)
    return

# Featured listings endpoint
@router.get("/featured", response_model=List[TractorSchema])
def get_featured_listings(
    limit: int = Query(6, ge=1),
    db: Session = Depends(get_db)
):
    # This assumes 'is_featured' is a field in the Tractor model. If not, it needs to be added.
    # For now, it will fetch all and limit, or you might need a different logic for 'featured'.
    featured_tractors = tractor_service.get_tractors(db, limit=limit) # Adjust as per your 'featured' logic
    # If 'is_featured' exists in the model and you want to filter by it:
    # featured_tractors = db.query(TractorModel).filter(TractorModel.is_featured == True).limit(limit).all()
    return featured_tractors 