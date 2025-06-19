from sqlalchemy.orm import Session
from sqlalchemy import or_, func # For JSON array contains-like operations if needed
from typing import List, Optional

from ..models.part import Part as PartModel
from ..schemas.part import PartCreate, PartUpdate, PartSchema
from ..schemas.user import UserSchema

class PartService:
    def get_part_by_id(self, db: Session, part_id: int) -> Optional[PartModel]:
        return db.query(PartModel).filter(PartModel.id == part_id).first()

    def get_parts(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        tractor_brand: Optional[str] = None, # Filter by a single brand compatibility
        condition: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        location: Optional[str] = None,
        seller_id: Optional[int] = None
    ) -> List[PartModel]:
        query = db.query(PartModel)

        if category:
            query = query.filter(PartModel.category.ilike(f"%{category}%"))
        if tractor_brand:
            # Search within the JSON array for a case-insensitive match
            # This requires a PostgreSQL specific operator '?' for jsonb, or a text search approach
            # For simpler implementations, consider direct string search or a more normalized DB design
            # For now, a simple 'like' on string representation of JSON might work for basic cases
            query = query.filter(func.lower(PartModel.tractor_brand_compatibility.astext).like(f'%"{tractor_brand.lower()}"%'))
        if condition:
            query = query.filter(PartModel.condition.ilike(f"%{condition}%"))
        if min_price:
            query = query.filter(PartModel.price >= min_price)
        if max_price:
            query = query.filter(PartModel.price <= max_price)
        if location:
            query = query.filter(PartModel.location.ilike(f"%{location}%"))
        if seller_id:
            query = query.filter(PartModel.seller_id == seller_id)

        return query.order_by(PartModel.created_at.desc()).offset(skip).limit(limit).all()

    def create_part(self, db: Session, part_in: PartCreate, seller_id: int) -> PartModel:
        db_part = PartModel(**part_in.model_dump(), seller_id=seller_id)
        db.add(db_part)
        db.commit()
        db.refresh(db_part)
        return db_part

    def update_part(self, db: Session, db_part: PartModel, part_in: PartUpdate) -> PartModel:
        update_data = part_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_part, key, value)
        db.add(db_part)
        db.commit()
        db.refresh(db_part)
        return db_part

    def delete_part(self, db: Session, part_id: int) -> Optional[PartModel]:
        db_part = self.get_part_by_id(db, part_id)
        if db_part:
            db.delete(db_part)
            db.commit()
        return db_part

part_service = PartService() # Instantiate the service
