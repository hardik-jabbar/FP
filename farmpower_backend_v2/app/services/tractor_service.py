from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.tractor import Tractor as TractorModel
from ..schemas.tractor import TractorCreate, TractorUpdate
# Assuming User model is not directly manipulated here beyond owner_id

class TractorService:
    def get_tractor_by_id(self, db: Session, tractor_id: int) -> Optional[TractorModel]:
        return db.query(TractorModel).filter(TractorModel.id == tractor_id).first()

    def get_tractors(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        brand: Optional[str] = None,
        location: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        owner_id: Optional[int] = None # Optional filter by owner
    ) -> List[TractorModel]:
        query = db.query(TractorModel)

        if brand:
            query = query.filter(TractorModel.brand.ilike(f"%{brand}%"))
        if location:
            query = query.filter(TractorModel.location.ilike(f"%{location}%"))
        if min_price:
            query = query.filter(TractorModel.price >= min_price)
        if max_price:
            query = query.filter(TractorModel.price <= max_price)
        if owner_id:
            query = query.filter(TractorModel.owner_id == owner_id)

        return query.offset(skip).limit(limit).all()

    def create_tractor(self, db: Session, tractor_in: TractorCreate, owner_id: int) -> TractorModel:
        db_tractor = TractorModel(**tractor_in.model_dump(), owner_id=owner_id)
        db.add(db_tractor)
        db.commit()
        db.refresh(db_tractor)
        return db_tractor

    def update_tractor(self, db: Session, db_tractor: TractorModel, tractor_in: TractorUpdate) -> TractorModel:
        update_data = tractor_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_tractor, key, value)
        db.add(db_tractor)
        db.commit()
        db.refresh(db_tractor)
        return db_tractor

    def delete_tractor(self, db: Session, tractor_id: int) -> Optional[TractorModel]:
        db_tractor = self.get_tractor_by_id(db, tractor_id)
        if db_tractor:
            db.delete(db_tractor)
            db.commit()
        return db_tractor

tractor_service = TractorService()
