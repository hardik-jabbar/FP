# FastAPI backend for crop yield calculation
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import geopandas as gpd
from shapely.geometry import shape, Polygon
import numpy as np
import json
import os
from datetime import datetime

app = FastAPI(title="FarmPower Crop Yield Calculator",
             description="Calculate expected crop yields based on field geometry and crop type")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class FieldGeometry(BaseModel):
    type: str
    coordinates: List[List[List[float]]]

class Field(BaseModel):
    name: str
    geometry: FieldGeometry
    crop_type: str
    soil_type: Optional[str] = "loam"
    irrigation: Optional[bool] = True

class YieldPrediction(BaseModel):
    field_name: str
    crop_type: str
    area_hectares: float
    expected_yield_tons: float
    yield_per_hectare: float
    confidence_score: float

# Crop yield factors (tons per hectare) - average yields in ideal conditions
CROP_YIELDS = {
    "wheat": 3.5,
    "corn": 9.5,
    "soybean": 3.0,
    "rice": 4.5,
    "cotton": 2.5,
    "potatoes": 35.0
}

# Soil quality factors (multiplier)
SOIL_FACTORS = {
    "clay": 0.85,
    "loam": 1.0,
    "sandy": 0.7,
    "silt": 0.9
}

# Irrigation factor
IRRIGATION_FACTOR = 1.3  # 30% yield increase with irrigation

def calculate_field_area(geometry: dict) -> float:
    """Calculate field area in hectares from GeoJSON geometry"""
    try:
        geom = shape(geometry)
        # Convert area from square meters to hectares
        area_hectares = geom.area / 10000
        return area_hectares
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid geometry: {str(e)}")

def predict_yield(field: Field) -> YieldPrediction:
    """Predict crop yield based on field characteristics"""
    # Calculate base yield
    area = calculate_field_area(field.geometry.dict())
    base_yield_per_hectare = CROP_YIELDS.get(field.crop_type.lower(), 0)
    
    # Apply soil factor
    soil_factor = SOIL_FACTORS.get(field.soil_type.lower(), 1.0)
    
    # Apply irrigation factor if irrigated
    irrigation_multiplier = IRRIGATION_FACTOR if field.irrigation else 1.0
    
    # Calculate total yield
    adjusted_yield_per_hectare = base_yield_per_hectare * soil_factor * irrigation_multiplier
    total_yield = adjusted_yield_per_hectare * area
    
    # Calculate confidence score (simplified)
    confidence_score = 0.85  # Base confidence
    
    return YieldPrediction(
        field_name=field.name,
        crop_type=field.crop_type,
        area_hectares=area,
        expected_yield_tons=total_yield,
        yield_per_hectare=adjusted_yield_per_hectare,
        confidence_score=confidence_score
    )

@app.post("/api/calculate-yield", response_model=YieldPrediction)
async def calculate_yield(field: Field):
    """Calculate expected yield for a field"""
    try:
        return predict_yield(field)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/crops")
async def get_crops():
    """Get list of supported crops and their base yields"""
    return CROP_YIELDS

@app.get("/api/soil-types")
async def get_soil_types():
    """Get list of supported soil types and their factors"""
    return SOIL_FACTORS