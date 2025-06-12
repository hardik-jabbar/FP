from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.dependencies import get_current_active_user, RoleChecker
from ..models.user import User as UserModel, UserRole
from ..models.tractor import Tractor as TractorModel
from ..schemas.tractor import Tractor as TractorSchema, TractorCreate, TractorUpdate
from ..services import tractor_service # tractor_service instance

router = APIRouter(
    prefix="/tractors",
    tags=["Tractors"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=TractorSchema)
async def list_new_tractor(
    tractor_in: TractorCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    List a new tractor for sale. Requires authentication.
    """
    return tractor_service.create_tractor(db=db, tractor=tractor_in, owner_id=current_user.id)

from typing import Optional # Ensure Optional is imported

@router.get("/", response_model=List[TractorSchema])
async def get_all_tractors(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(default=10, le=100),
    brand: Optional[str] = Query(None, description="Filter by brand name (case-insensitive)"),
    location: Optional[str] = Query(None, description="Filter by location (case-insensitive)"),
    min_price: Optional[float] = Query(None, alias="minPrice", gt=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, alias="maxPrice", gt=0, description="Maximum price filter")
):
    """
    Get a list of all available tractors. Supports filtering by brand, location, and price range.
    No authentication required.
    """
    if max_price is not None and min_price is not None and max_price < min_price:
        raise HTTPException(status_code=400, detail="maxPrice cannot be less than minPrice.")

    tractors = tractor_service.get_tractors(
        db,
        skip=skip,
        limit=limit,
        brand=brand,
        location=location,
        min_price=min_price,
        max_price=max_price
    )
    return tractors

@router.get("/{tractor_id}", response_model=TractorSchema)
async def get_tractor_details(
    tractor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific tractor. No authentication required.
    """
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id=tractor_id)
    if db_tractor is None:
        raise HTTPException(status_code=404, detail="Tractor not found")
    return db_tractor

@router.put("/{tractor_id}", response_model=TractorSchema)
async def update_tractor_listing(
    tractor_id: int,
    tractor_in: TractorUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update an existing tractor listing.
    Requires authentication. User must be owner or admin.
    """
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id=tractor_id)
    if db_tractor is None:
        raise HTTPException(status_code=404, detail="Tractor not found")

    if db_tractor.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to update this tractor listing")

    return tractor_service.update_tractor(db=db, db_tractor=db_tractor, tractor_in=tractor_in)

@router.delete("/{tractor_id}", status_code=204)
async def remove_tractor_listing(
    tractor_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Remove a tractor listing.
    Requires authentication. User must be owner or admin.
    """
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id=tractor_id)
    if db_tractor is None:
        raise HTTPException(status_code=404, detail="Tractor not found")

    if db_tractor.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this tractor listing")

    tractor_service.delete_tractor(db=db, tractor_id=tractor_id)
    return # Returns 204 No Content by default on success

from fastapi import File, UploadFile # For file uploads
from ..services import s3_service # Import the S3 service

@router.post("/{tractor_id}/upload-image/", response_model=TractorSchema)
async def upload_tractor_image(
    tractor_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Upload an image for a tractor. The image will be added to the tractor's image_urls list.
    Requires authentication. User must be the owner of the tractor or an admin.
    """
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id=tractor_id)
    if not db_tractor:
        raise HTTPException(status_code=404, detail="Tractor not found")

    # Authorization check
    if db_tractor.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to upload images for this tractor")

    contents = await file.read() # Read file content
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty")

    # Use file.file for aiobotocore if it expects a file-like object for streaming
    # For this example, we're passing bytes (contents) to s3_service
    image_url = await s3_service.upload_file_to_s3(contents, file.filename)

    if not image_url:
        raise HTTPException(status_code=500, detail="Failed to upload image to S3")

    # Update tractor's image_urls
    # current_image_urls = list(db_tractor.image_urls) if db_tractor.image_urls else [] # Ensure it's a mutable list
    # The above line might cause issues if db_tractor.image_urls is already a Python list due to ORM config,
    # or if it's None/JSONB that needs careful handling.
    # Let's fetch it fresh or handle mutability carefully.

    # A safer way to handle JSON field update, especially if ORM tracks changes.
    # Re-fetch the tractor to ensure the session is tracking it if needed, though db_tractor is from session.

    # Initialize image_urls if None or not a list (though JSON type should handle list storage)
    if db_tractor.image_urls is None:
        db_tractor.image_urls = []

    # Ensure it's a list (SQLAlchemy JSON type might return it as a list already)
    if not isinstance(db_tractor.image_urls, list):
        # This case should ideally not happen if the JSON column is consistently used for lists.
        # If it can be other JSON types, more complex handling is needed.
        # For now, assuming it's meant to be a list or becomes one.
        db_tractor.image_urls = [str(url) for url in list(db_tractor.image_urls or [])]


    db_tractor.image_urls.append(image_url) # Append new URL

    # Mark the field as modified for SQLAlchemy to pick up the change in mutable JSON types
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(db_tractor, "image_urls")

    db.add(db_tractor) # Add to session to ensure it's tracked
    db.commit()
    db.refresh(db_tractor)

    return db_tractor
