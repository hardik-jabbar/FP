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

        if owner_id is not None:
            query = query.filter(TractorModel.owner_id == owner_id)
        if brand:
            query = query.filter(TractorModel.brand.ilike(f"%{brand}%"))
        if location:
            query = query.filter(TractorModel.location.ilike(f"%{location}%"))
        if min_price is not None:
            query = query.filter(TractorModel.price >= min_price)
        if max_price is not None:
            query = query.filter(TractorModel.price <= max_price)

        return query.order_by(TractorModel.created_at.desc()).offset(skip).limit(limit).all()

    def create_tractor(self, db: Session, tractor_in: TractorCreate, owner_id: int) -> TractorModel:
        tractor_data = tractor_in.model_dump() # Pydantic V2
        db_tractor = TractorModel(**tractor_data, owner_id=owner_id)
        db.add(db_tractor)
        db.commit()
        db.refresh(db_tractor)
        return db_tractor

    def update_tractor(self, db: Session, db_tractor: TractorModel, tractor_in: TractorUpdate) -> TractorModel:
        update_data = tractor_in.model_dump(exclude_unset=True) # Pydantic V2, exclude_unset for partial updates

        for field, value in update_data.items():
            setattr(db_tractor, field, value)

        db.add(db_tractor) # Mark as dirty
        db.commit()
        db.refresh(db_tractor)
        return db_tractor

    def delete_tractor(self, db: Session, tractor_id: int) -> Optional[TractorModel]:
        db_tractor = self.get_tractor_by_id(db, tractor_id)
        if db_tractor:
            db.delete(db_tractor)
            db.commit()
        return db_tractor # Returns the deleted object or None

tractor_service = TractorService() # Instantiate the service
