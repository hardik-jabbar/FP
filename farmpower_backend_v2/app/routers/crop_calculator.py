from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.crop_calculator import CropCalculation
from ..schemas.crop_calculator import CropProfitRequest, CropProfitResponse, CropCalculationHistory

router = APIRouter(tags=["crop-profit"])

@router.post("/calculate", response_model=CropProfitResponse)
async def calculate_profit(request: CropProfitRequest):
    """Calculate profit for a crop based on input parameters."""
    try:
        # Calculate total costs
        per_acre_costs = (
            request.seed_cost_per_acre +
            request.fertilizer_cost_per_acre +
            request.pesticide_cost_per_acre
        )
        total_cost = (per_acre_costs * request.field_area_acres +
                     request.labor_cost_total +
                     request.other_costs_total)

        # Calculate revenue
        revenue = (request.expected_yield_per_acre *
                  request.field_area_acres *
                  request.market_price_per_unit)

        # Calculate profit and margin
        profit = revenue - total_cost
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0

        return CropProfitResponse(
            total_cost=total_cost,
            revenue=revenue,
            profit=profit,
            profit_margin=profit_margin
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/save")
async def save_calculation(
    calculation: CropCalculationHistory,
    db: Session = Depends(get_db)
):
    """Save a crop profit calculation to the database."""
    try:
        db_calculation = CropCalculation(
            crop_name=calculation.crop_type,
            field_area=calculation.field_area,
            total_cost=calculation.total_cost,
            revenue=calculation.revenue,
            profit=calculation.profit,
            created_at=datetime.utcnow()
        )
        db.add(db_calculation)
        db.commit()
        db.refresh(db_calculation)
        return {"message": "Calculation saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history", response_model=List[CropCalculationHistory])
async def get_calculation_history(db: Session = Depends(get_db)):
    """Get history of crop profit calculations."""
    try:
        calculations = db.query(CropCalculation).order_by(
            CropCalculation.created_at.desc()
        ).limit(10).all()
        
        return [
            CropCalculationHistory(
                crop_type=calc.crop_name,
                field_area=calc.field_area,
                total_cost=calc.total_cost,
                revenue=calc.revenue,
                profit=calc.profit,
                created_at=calc.created_at
            ) for calc in calculations
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 