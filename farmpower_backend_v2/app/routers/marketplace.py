from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.tractor import Tractor
from ..models.part import Part
from ..schemas.tractor import TractorSchema, TractorCreate, TractorUpdate
from ..schemas.part import PartSchema, PartCreate, PartUpdate
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix="/marketplace",
    tags=["marketplace"]
)

# Tractor endpoints
@router.get("/tractors", response_model=List[TractorSchema])
def get_tractors(
    skip: int = 0,
    limit: int = 10,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    condition: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Tractor)
    
    if brand:
        query = query.filter(Tractor.brand == brand)
    if min_price:
        query = query.filter(Tractor.price >= min_price)
    if max_price:
        query = query.filter(Tractor.price <= max_price)
    if condition:
        query = query.filter(Tractor.condition == condition)
    
    return query.offset(skip).limit(limit).all()

@router.get("/tractors/{tractor_id}", response_model=TractorSchema)
def get_tractor(tractor_id: int, db: Session = Depends(get_db)):
    tractor = db.query(Tractor).filter(Tractor.id == tractor_id).first()
    if not tractor:
        raise HTTPException(status_code=404, detail="Tractor not found")
    return tractor

@router.post("/tractors", response_model=TractorSchema)
def create_tractor(
    tractor: TractorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_tractor = Tractor(**tractor.dict(), seller_id=current_user.id)
    db.add(db_tractor)
    db.commit()
    db.refresh(db_tractor)
    return db_tractor

@router.put("/tractors/{tractor_id}", response_model=TractorSchema)
def update_tractor(
    tractor_id: int,
    tractor: TractorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_tractor = db.query(Tractor).filter(Tractor.id == tractor_id).first()
    if not db_tractor:
        raise HTTPException(status_code=404, detail="Tractor not found")
    if db_tractor.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this tractor")
    
    for key, value in tractor.dict(exclude_unset=True).items():
        setattr(db_tractor, key, value)
    
    db.commit()
    db.refresh(db_tractor)
    return db_tractor

# Part endpoints
@router.get("/parts", response_model=List[PartSchema])
def get_parts(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Part)
    
    if category:
        query = query.filter(Part.category == category)
    if brand:
        query = query.filter(Part.brand == brand)
    if min_price:
        query = query.filter(Part.price >= min_price)
    if max_price:
        query = query.filter(Part.price <= max_price)
    
    return query.offset(skip).limit(limit).all()

@router.get("/parts/{part_id}", response_model=PartSchema)
def get_part(part_id: int, db: Session = Depends(get_db)):
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part

@router.post("/parts", response_model=PartSchema)
def create_part(
    part: PartCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_part = Part(**part.dict(), seller_id=current_user.id)
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part

@router.put("/parts/{part_id}", response_model=PartSchema)
def update_part(
    part_id: int,
    part: PartUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_part = db.query(Part).filter(Part.id == part_id).first()
    if not db_part:
        raise HTTPException(status_code=404, detail="Part not found")
    if db_part.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this part")
    
    for key, value in part.dict(exclude_unset=True).items():
        setattr(db_part, key, value)
    
    db.commit()
    db.refresh(db_part)
    return db_part

# Featured listings endpoint
@router.get("/featured", response_model=List[TractorSchema])
def get_featured_listings(
    limit: int = 6,
    db: Session = Depends(get_db)
):
    featured_tractors = db.query(Tractor)\
        .filter(Tractor.is_featured == True)\
        .limit(limit)\
        .all()
    return featured_tractors 