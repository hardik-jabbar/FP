from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.tractor import Tractor as TractorModel
from ..schemas.tractor import TractorCreate, TractorUpdate
# User model might be needed if we do complex checks involving owner properties, not directly for now.
# from ..models.user import User as UserModel

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
        max_price: Optional[float] = None
    ) -> List[TractorModel]:
        query = db.query(TractorModel)

        if brand:
            query = query.filter(TractorModel.brand.ilike(f"%{brand}%"))
        if location:
            query = query.filter(TractorModel.location.ilike(f"%{location}%"))
        if min_price is not None:
            query = query.filter(TractorModel.price >= min_price)
        if max_price is not None:
            query = query.filter(TractorModel.price <= max_price)

        return query.order_by(TractorModel.created_at.desc()).offset(skip).limit(limit).all()

    def create_tractor(self, db: Session, tractor: TractorCreate, owner_id: int) -> TractorModel:
        # Pydantic V2 uses model_dump()
        tractor_data = tractor.model_dump()
        db_tractor = TractorModel(**tractor_data, owner_id=owner_id)
        db.add(db_tractor)
        db.commit()
        db.refresh(db_tractor)
        return db_tractor

    def update_tractor(self, db: Session, db_tractor: TractorModel, tractor_in: TractorUpdate) -> TractorModel:
        # Pydantic V2 uses model_dump()
        update_data = tractor_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tractor, field, value)
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

# Instantiate the service
tractor_service = TractorService()
