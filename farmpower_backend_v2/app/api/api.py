from fastapi import APIRouter
from app.api.endpoints import users, equipment

api_router = APIRouter()

# Include all API endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(equipment.router, tags=["equipment"])