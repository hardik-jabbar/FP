from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..models.crop import Crop as CropModel
from ..schemas.crop import CropCreate, CropUpdate, ProfitCalculationResult

class CropService:
    def get_crop_by_id(self, db: Session, crop_id: int) -> Optional[CropModel]:
        return db.query(CropModel).filter(CropModel.id == crop_id).first()

    def get_crops_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[CropModel]:
        return db.query(CropModel).filter(CropModel.user_id == user_id).order_by(CropModel.name).offset(skip).limit(limit).all()

    def get_crops_by_field(self, db: Session, field_id: int, skip: int = 0, limit: int = 100) -> List[CropModel]:
        # This might be useful if listing crops specifically associated with a field
        return db.query(CropModel).filter(CropModel.field_id == field_id).order_by(CropModel.name).offset(skip).limit(limit).all()

    def create_crop(self, db: Session, crop_in: CropCreate, user_id: int) -> CropModel:
        crop_data = crop_in.model_dump()
        db_crop = CropModel(**crop_data, user_id=user_id)
        db.add(db_crop)
        db.commit()
        db.refresh(db_crop)
        return db_crop

    def update_crop(self, db: Session, db_crop: CropModel, crop_in: CropUpdate) -> CropModel:
        update_data = crop_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_crop, field, value)
        db.add(db_crop) # Mark as dirty
        db.commit()
        db.refresh(db_crop)
        return db_crop

    def delete_crop(self, db: Session, crop_id: int) -> Optional[CropModel]:
        db_crop = self.get_crop_by_id(db, crop_id)
        if db_crop:
            db.delete(db_crop)
            db.commit()
        return db_crop

    def calculate_profitability(self, crop: CropModel) -> ProfitCalculationResult:
        cost_breakdown: Dict[str, float] = {
            "seed": crop.seed_cost_per_hectare,
            "fertilizer": crop.fertilizer_cost_per_hectare,
            "pesticide": crop.pesticide_cost_per_hectare or 0.0,
            "machinery": crop.machinery_cost_per_hectare or 0.0,
            "labor": crop.labor_cost_per_hectare or 0.0,
            "other": crop.other_costs_per_hectare or 0.0,
        }
        total_costs_per_hectare = sum(cost_breakdown.values())

        revenue_details: Dict[str, Any] = {
            "expected_yield_per_hectare": crop.expected_yield_per_hectare,
            "yield_unit": crop.yield_unit,
            "market_price_per_unit": crop.market_price_per_unit,
        }
        total_revenue_per_hectare = crop.expected_yield_per_hectare * crop.market_price_per_unit

        profit_or_loss_per_hectare = total_revenue_per_hectare - total_costs_per_hectare

        # profit_margin_percentage = 0.0
        # if total_revenue_per_hectare > 0:
        #     profit_margin_percentage = (profit_or_loss_per_hectare / total_revenue_per_hectare) * 100
        # elif total_revenue_per_hectare == 0 and total_costs_per_hectare == 0:
        #     profit_margin_percentage = 0.0
        # elif total_revenue_per_hectare == 0 and total_costs_per_hectare > 0: # Pure loss
        #     profit_margin_percentage = -100.0 # Or some other indicator of loss relative to cost

        return ProfitCalculationResult(
            crop_name=crop.name,
            crop_variety=crop.crop_variety,
            total_revenue_per_hectare=round(total_revenue_per_hectare, 2),
            total_costs_per_hectare=round(total_costs_per_hectare, 2),
            profit_or_loss_per_hectare=round(profit_or_loss_per_hectare, 2),
            # profit_margin_percentage=round(profit_margin_percentage, 2),
            cost_breakdown=cost_breakdown,
            revenue_details=revenue_details
        )

crop_service = CropService() # Instantiate the service
