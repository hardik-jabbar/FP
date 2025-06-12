from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import Base, engine
# Import all models from the models package to ensure they are registered with Base
from app import models

# Import all routers
from app.routers import users as user_router
from app.routers import tractors as tractor_router
from app.routers import fields as field_router
from app.routers import crops as crop_router
from app.routers import services as service_booking_router
from app.routers import parts as part_router
from app.routers import notifications as notification_router
from app.routers import messages as message_router
from app.routers import admin as admin_router
from app.routers import crop_calculator as crop_calculator_router
from app.routers import marketplace

# Create database tables (if they don't exist yet)
# This is useful for development. For production, use migrations (e.g., Alembic).
Base.metadata.create_all(bind=engine, checkfirst=True) # Ensures all imported models' tables are created

app = FastAPI(title="FarmPower Backend v2")

# Get the absolute path to the 'FARMPOWER' directory, which is at the root of the project.
# The current file is in farmpower_backend_v2/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
farmpower_dir = os.path.join(project_root, 'FARMPOWER')

# Serve shop.html
@app.get("/shop", response_class=FileResponse)
async def read_shop():
    return FileResponse(os.path.join(farmpower_dir, 'shop.html'))

# Serve other html files
@app.get("/{page_name}.html", response_class=FileResponse)
async def read_html(page_name: str):
    file_path = os.path.join(farmpower_dir, f"{page_name}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")


# Mount the 'assets' directory inside 'FARMPOWER' to the '/assets' path
app.mount("/assets", StaticFiles(directory=os.path.join(farmpower_dir, 'assets')), name="assets")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(user_router.router)
app.include_router(tractor_router.router)
app.include_router(field_router.router)
app.include_router(crop_router.router)
app.include_router(service_booking_router.router)
app.include_router(part_router.router)
app.include_router(notification_router.router)
app.include_router(message_router.router)
app.include_router(admin_router.router)
app.include_router(crop_calculator_router.router, prefix="/api/crop-profit", tags=["crop-calculator"])
app.include_router(marketplace.router)

@app.get("/")
async def root():
    return {"message": "Welcome to FarmPower Backend v2"}
