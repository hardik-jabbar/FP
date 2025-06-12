from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.field import Field as FieldModel
from ..models.land_usage_plan import LandUsagePlan as LandUsagePlanModel
from ..schemas.field import FieldCreate, FieldUpdate
# Using FieldSchema for responses, FieldCreate/Update for C/U ops
from ..schemas.land_usage_plan import LandUsagePlanCreate, LandUsagePlanUpdate
# Using LandUsagePlanSchema for responses

class FieldService:
    # --- Field Methods ---
    def get_field_by_id(self, db: Session, field_id: int) -> Optional[FieldModel]:
        return db.query(FieldModel).filter(FieldModel.id == field_id).first()

    def get_fields_by_owner(self, db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[FieldModel]:
        return db.query(FieldModel).filter(FieldModel.owner_id == owner_id).offset(skip).limit(limit).all()

    def create_field(self, db: Session, field_in: FieldCreate, owner_id: int) -> FieldModel:
        field_data = field_in.model_dump()
        db_field = FieldModel(**field_data, owner_id=owner_id)
        db.add(db_field)
        db.commit()
        db.refresh(db_field)
        return db_field

    def update_field(self, db: Session, db_field: FieldModel, field_in: FieldUpdate) -> FieldModel:
        update_data = field_in.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(db_field, field_name, value)
        db.add(db_field)
        db.commit()
        db.refresh(db_field)
        return db_field

    def delete_field(self, db: Session, field_id: int) -> Optional[FieldModel]:
        db_field = self.get_field_by_id(db, field_id)
        if db_field:
            db.delete(db_field)
            db.commit()
        return db_field

    # --- LandUsagePlan Methods ---
    def get_plan_by_id(self, db: Session, plan_id: int) -> Optional[LandUsagePlanModel]:
        return db.query(LandUsagePlanModel).filter(LandUsagePlanModel.id == plan_id).first()

    def get_plans_for_field(self, db: Session, field_id: int, skip: int = 0, limit: int = 100) -> List[LandUsagePlanModel]:
        return db.query(LandUsagePlanModel).filter(LandUsagePlanModel.field_id == field_id).offset(skip).limit(limit).all()

    def create_land_usage_plan(self, db: Session, plan_in: LandUsagePlanCreate, field_id: int) -> LandUsagePlanModel:
        plan_data = plan_in.model_dump()
        db_plan = LandUsagePlanModel(**plan_data, field_id=field_id)
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan

    def update_land_usage_plan(self, db: Session, db_plan: LandUsagePlanModel, plan_in: LandUsagePlanUpdate) -> LandUsagePlanModel:
        update_data = plan_in.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(db_plan, field_name, value)
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan

    def delete_land_usage_plan(self, db: Session, plan_id: int) -> Optional[LandUsagePlanModel]:
        db_plan = self.get_plan_by_id(db, plan_id)
        if db_plan:
            db.delete(db_plan)
            db.commit()
        return db_plan

field_service = FieldService()
