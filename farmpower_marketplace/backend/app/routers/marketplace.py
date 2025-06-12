from fastapi import APIRouter, Body, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..schemas import product as product_schema
from ..services import marketplace_service
from ..core.database import SessionLocal

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tractors", response_model=List[product_schema.Tractor])
def get_tractors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tractors = marketplace_service.get_tractors(db, skip=skip, limit=limit)
    return tractors

@router.get("/parts", response_model=List[product_schema.Part])
def get_parts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    parts = marketplace_service.get_parts(db, skip=skip, limit=limit)
    return parts

@router.get("/tractors/{id}", response_model=product_schema.Tractor)
def get_tractor(id: int, db: Session = Depends(get_db)):
    db_tractor = marketplace_service.get_tractor(db, tractor_id=id)
    if db_tractor is None:
        raise HTTPException(status_code=404, detail="Tractor not found")
    return db_tractor

@router.get("/parts/{id}", response_model=product_schema.Part)
def get_part(id: int, db: Session = Depends(get_db)):
    db_part = marketplace_service.get_part(db, part_id=id)
    if db_part is None:
        raise HTTPException(status_code=404, detail="Part not found")
    return db_part

@router.post("/tractors", response_model=product_schema.Tractor)
def create_tractor(tractor: product_schema.TractorCreate, db: Session = Depends(get_db)):
    return marketplace_service.create_tractor(db=db, tractor=tractor)

@router.put("/tractors/{id}", response_model=product_schema.Tractor)
def update_tractor(id: int, tractor: product_schema.TractorCreate, db: Session = Depends(get_db)):
    # This should be implemented in the service
    db_tractor = marketplace_service.get_tractor(db, tractor_id=id)
    if db_tractor is None:
        raise HTTPException(status_code=404, detail="Tractor not found")
    # A simple update, a real implementation would be more robust
    for var, value in vars(tractor).items():
        setattr(db_tractor, var, value) if value else None
    db.add(db_tractor)
    db.commit()
    db.refresh(db_tractor)
    return db_tractor

@router.delete("/tractors/{id}")
def delete_tractor(id: int, db: Session = Depends(get_db)):
    db_tractor = marketplace_service.get_tractor(db, tractor_id=id)
    if db_tractor is None:
        raise HTTPException(status_code=404, detail="Tractor not found")
    db.delete(db_tractor)
    db.commit()
    return {"message": f"Tractor {id} deleted"}

@router.post("/parts", response_model=product_schema.Part)
def create_part(part: product_schema.PartCreate, db: Session = Depends(get_db)):
    return marketplace_service.create_part(db=db, part=part)

@router.put("/parts/{id}", response_model=product_schema.Part)
def update_part(id: int, part: product_schema.PartCreate, db: Session = Depends(get_db)):
    # This should be implemented in the service
    db_part = marketplace_service.get_part(db, part_id=id)
    if db_part is None:
        raise HTTPException(status_code=404, detail="Part not found")
    for var, value in vars(part).items():
        setattr(db_part, var, value) if value else None
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part

@router.delete("/parts/{id}")
def delete_part(id: int, db: Session = Depends(get_db)):
    db_part = marketplace_service.get_part(db, part_id=id)
    if db_part is None:
        raise HTTPException(status_code=404, detail="Part not found")
    db.delete(db_part)
    db.commit()
    return {"message": f"Part {id} deleted"}
