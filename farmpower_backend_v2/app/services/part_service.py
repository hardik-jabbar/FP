from sqlalchemy.orm import Session
from sqlalchemy import or_ # For JSON array contains-like operations if needed
from typing import List, Optional

from ..models.part import Part as PartModel
from ..schemas.part import PartCreate, PartUpdate

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
        if condition:
            query = query.filter(PartModel.condition == condition)
        if min_price is not None:
            query = query.filter(PartModel.price >= min_price)
        if max_price is not None:
            query = query.filter(PartModel.price <= max_price)
        if location:
            query = query.filter(PartModel.location.ilike(f"%{location}%"))
        if seller_id is not None:
            query = query.filter(PartModel.seller_id == seller_id)

        # Filtering by tractor_brand in a JSON list:
        # This is a simplified example. For robust JSON querying, database-specific functions
        # like PostgreSQL's JSONB operators (@>, ?, ?&, ?|) are more powerful.
        # SQLAlchemy can express some of these, e.g., using .contains() for simple array membership
        # or custom SQL constructs.
        if tractor_brand:
            # Simple string matching if tractor_brand_compatibility was a simple string.
            # For JSON array, this requires a more specific approach.
            # Example for PostgreSQL JSONB: query = query.filter(PartModel.tractor_brand_compatibility.op('@>')([tractor_brand]))
            # For a generic approach that might work on simple JSON text in SQLite/MySQL (less efficient):
            query = query.filter(PartModel.tractor_brand_compatibility.astext.ilike(f'%"{tractor_brand}"%'))


        return query.order_by(PartModel.created_at.desc()).offset(skip).limit(limit).all()

    def create_part(self, db: Session, part_in: PartCreate, seller_id: int) -> PartModel:
        part_data = part_in.model_dump()
        db_part = PartModel(**part_data, seller_id=seller_id)
        db.add(db_part)
        db.commit()
        db.refresh(db_part)
        return db_part

    def update_part(self, db: Session, db_part: PartModel, part_in: PartUpdate) -> PartModel:
        update_data = part_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_part, field, value)
        db.add(db_part) # Mark as dirty
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
