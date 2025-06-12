from fastapi import FastAPI

from app.core.db import Base, engine
from app.models.user import User
from app.models.tractor import Tractor
from app.models.field import Field
from app.models.land_usage_plan import LandUsagePlan
from app.models.crop import Crop

from app.routers import users as user_router
from app.routers import tractors as tractor_router
from app.routers import fields as field_router
from app.routers import crops as crop_router

from app.core.socket_manager import socket_app as farmpower_socket_app

# Create database tables (if they don't exist)
# Note: For production, use Alembic migrations instead of this
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FarmPower API")

# Mount the Socket.IO app for WebSocket connections at /ws
app.mount("/ws", farmpower_socket_app)

# Include routers
app.include_router(user_router.router)
app.include_router(tractor_router.router)
app.include_router(field_router.router)
app.include_router(crop_router.router)


@app.get('/')
async def root():
    return {'message': 'Welcome to FarmPower API'}
