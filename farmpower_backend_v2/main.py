import os
import sys
import logging
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import rate limit middleware after modifying sys.path
from middleware.rate_limit import rate_limit_middleware

# Load environment variables
load_dotenv()

# Get configuration from environment variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database and models using relative imports
from .app.database import Base, engine
# Import all models to ensure they are registered with Base
from .app import models

# Import all routers using relative imports
from .app.routers import users as user_router
from .app.routers import tractors as tractor_router
from .app.routers import fields as field_router
from .app.routers import crops as crop_router
from .app.routers import services as service_booking_router
from .app.routers import parts as part_router
from .app.routers import notifications as notification_router
from .app.routers import messages as message_router
from .app.routers import admin as admin_router
from .app.routers import crop_calculator as crop_calculator_router
from .app.routers import auth_json as auth_json_router
from .app.routers import marketplace

# Create database tables (if they don't exist yet)
# This is useful for development. For production, use migrations (e.g., Alembic).
Base.metadata.create_all(bind=engine, checkfirst=True) # Ensures all imported models' tables are created

# Security middleware for adding security headers
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self' https: wss:; frame-ancestors 'none';"
        return response

# Initialize FastAPI app
app = FastAPI(
    title="FarmPower API",
    description="FarmPower Backend API",
    version="1.0.0",
    docs_url="/docs" if os.getenv('ENVIRONMENT') != 'production' else None,
    redoc_url="/redoc" if os.getenv('ENVIRONMENT') != 'production' else None
)

# Health check endpoint
@app.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring and container orchestration."""
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "host": HOST,
        "port": PORT,
        "debug": ENVIRONMENT == "development"
    }

# Get the absolute path to the 'FARMPOWER' directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
farmpower_dir = os.path.join(project_root, 'FARMPOWER')

# Log the paths for debugging
logger.info(f"Project root: {project_root}")
logger.info(f"FARMPOWER directory: {farmpower_dir}")
logger.info(f"Directory exists: {os.path.exists(farmpower_dir)}")

# Configure CORS first - allow all origins
allowed_origins = [origin.strip() for origin in os.getenv('ALLOWED_ORIGINS', '').split(',') if origin.strip()]
if not allowed_origins:
    allowed_origins = ["http://localhost:3000"]  # Default for development

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=600,  # 10 minutes
)

# Redirect HTTP to HTTPS in production
if os.getenv('ENVIRONMENT') == 'production':
    app.add_middleware(HTTPSRedirectMiddleware)

# Add rate limiting middleware
app = rate_limit_middleware(app)

# Mount static files (e.g., CSS, JS, images) from the 'assets' directory
assets_dir = os.path.join(farmpower_dir, 'assets')
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    logger.info("Mounted assets directory for static files")
else:
    logger.warning(f"Assets directory not found: {assets_dir}")

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
app.include_router(auth_json_router.router)
app.include_router(marketplace.router)

# Serve index.html for the root path
@app.get("/", response_class=HTMLResponse)
async def read_root():
    file_path = os.path.join(farmpower_dir, 'index.html')
    logger.info(f"Serving index.html from: {file_path}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Index page not found")
    return FileResponse(file_path)

# Serve other HTML files (e.g., marketplace.html, shop.html)
@app.get("/{page_name}.html", response_class=HTMLResponse)
async def read_html(page_name: str):
    file_path = os.path.join(farmpower_dir, f"{page_name}.html")
    logger.info(f"Serving {page_name}.html from: {file_path}")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail=f"Page {page_name}.html not found")

# Catch-all route for frontend routes (e.g., direct navigation to /marketplace or /shop)
@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_frontend(path: str):
    # Try to serve a corresponding HTML file (e.g., /marketplace -> marketplace.html)
    html_file_path = os.path.join(farmpower_dir, f"{path}.html")
    if os.path.exists(html_file_path) and os.path.isfile(html_file_path):
        logger.info(f"Serving corresponding HTML file for /{path}: {html_file_path}")
        return FileResponse(html_file_path)

    # If not an HTML file, try to serve the exact path as a static file (e.g., CSS, JS)
    static_file_path = os.path.join(farmpower_dir, path)
    if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
        logger.info(f"Serving exact static file: {static_file_path}")
        return FileResponse(static_file_path)

    # If none of the above, serve index.html as a fallback for client-side routing
    index_path = os.path.join(farmpower_dir, 'index.html')
    if os.path.exists(index_path):
        logger.info(f"Fallback to index.html for path: {path}")
        return FileResponse(index_path)
    
    logger.warning(f"Neither HTML file nor static file found, and index.html not available for path: {path}")
    raise HTTPException(status_code=404, detail=f"File or page not found for path: {path}")
