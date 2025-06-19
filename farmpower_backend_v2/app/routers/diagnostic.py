from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.diagnostic import DiagnosticReport, MaintenanceSchedule
from ..schemas.diagnostic import DiagnosticReportSchema, MaintenanceScheduleSchema
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix="/diagnostic",
    tags=["diagnostic"]
)

# Dummy data for testing
DUMMY_DIAGNOSTIC_REPORTS = [
    {
        "tractor_id": 1,
        "report_type": "Engine",
        "status": "Warning",
        "description": "Engine oil pressure below normal range",
        "severity": "Medium",
        "recommendation": "Check oil level and pressure sensor"
    },
    {
        "tractor_id": 2,
        "report_type": "Transmission",
        "status": "Critical",
        "description": "Transmission fluid temperature exceeding normal range",
        "severity": "High",
        "recommendation": "Immediate service required"
    }
]

DUMMY_MAINTENANCE_SCHEDULES = [
    {
        "tractor_id": 1,
        "maintenance_type": "Regular Service",
        "due_date": "2024-04-15",
        "description": "Regular maintenance including oil change and filter replacement",
        "status": "Pending"
    },
    {
        "tractor_id": 2,
        "maintenance_type": "Major Service",
        "due_date": "2024-05-01",
        "description": "Major service including transmission fluid change and hydraulic system check",
        "status": "Scheduled"
    }
]

@router.post("/seed-dummy-data")
def seed_dummy_data(db: Session = Depends(get_db)):
    """Endpoint to seed dummy diagnostic data for testing"""
    try:
        # Add dummy diagnostic reports
        for report_data in DUMMY_DIAGNOSTIC_REPORTS:
            report = DiagnosticReport(**report_data)
            db.add(report)
        
        # Add dummy maintenance schedules
        for schedule_data in DUMMY_MAINTENANCE_SCHEDULES:
            schedule = MaintenanceSchedule(**schedule_data)
            db.add(schedule)
        
        db.commit()
        return {"message": "Dummy diagnostic data seeded successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ... existing code ... 