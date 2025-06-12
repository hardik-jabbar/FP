from sqlalchemy.orm import Session
from .. import models, schemas

# Tractors
def get_tractors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.product.Tractor).offset(skip).limit(limit).all()

def get_tractor(db: Session, tractor_id: int):
    return db.query(models.product.Tractor).filter(models.product.Tractor.id == tractor_id).first()

def create_tractor(db: Session, tractor: schemas.product.TractorCreate):
    db_tractor = models.product.Tractor(**tractor.dict())
    db.add(db_tractor)
    db.commit()
    db.refresh(db_tractor)
    return db_tractor

# Parts
def get_parts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.product.Part).offset(skip).limit(limit).all()

def get_part(db: Session, part_id: int):
    return db.query(models.product.Part).filter(models.product.Part.id == part_id).first()

def create_part(db: Session, part: schemas.product.PartCreate):
    db_part = models.product.Part(**part.dict())
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part 