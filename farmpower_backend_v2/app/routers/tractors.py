from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified


from ..core.db import get_db
from ..core.dependencies import get_current_active_user # Assuming RoleChecker is not needed for basic CRUD auth by owner/admin
from ..models.user import User as UserModel, UserRole # UserRole for checking admin
from ..models.tractor import Tractor as TractorModel
from ..schemas.tractor import TractorSchema, TractorCreate, TractorUpdate
from ..services import tractor_service, s3_service # Import s3_service for image upload

router = APIRouter(
    prefix="/tractors",
    tags=["Tractors"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=TractorSchema, status_code=status.HTTP_201_CREATED)
async def create_new_tractor_listing(
    tractor_in: TractorCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    List a new tractor for sale. Requires authentication.
    The owner_id will be automatically set to the current authenticated user.
    """
    return tractor_service.create_tractor(db=db, tractor_in=tractor_in, owner_id=current_user.id)

@router.get("/", response_model=List[TractorSchema])
async def get_all_tractor_listings(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=200), # Max 200 items
    brand: Optional[str] = Query(None, description="Filter by brand name (case-insensitive)"),
    location: Optional[str] = Query(None, description="Filter by location (case-insensitive)"),
    min_price: Optional[float] = Query(None, alias="minPrice", gt=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, alias="maxPrice", gt=0, description="Maximum price filter"),
    owner_id: Optional[int] = Query(None, description="Filter by owner's user ID")
):
    """
    Get a list of all available tractors. Supports filtering and pagination.
    No authentication required for browsing.
    """
    if max_price is not None and min_price is not None and max_price < min_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="maxPrice cannot be less than minPrice.")

    tractors = tractor_service.get_tractors(
        db, skip=skip, limit=limit, brand=brand, location=location,
        min_price=min_price, max_price=max_price, owner_id=owner_id
    )
    return tractors

@router.get("/{tractor_id}", response_model=TractorSchema)
async def get_tractor_listing_details(
    tractor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific tractor listing. No authentication required.
    """
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id=tractor_id)
    if db_tractor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tractor not found")
    return db_tractor

@router.put("/{tractor_id}", response_model=TractorSchema)
async def update_existing_tractor_listing(
    tractor_id: int,
    tractor_in: TractorUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update an existing tractor listing.
    Requires authentication. User must be the owner or an ADMIN.
    """
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id=tractor_id)
    if db_tractor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tractor not found")

    if db_tractor.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this tractor listing")

    return tractor_service.update_tractor(db=db, db_tractor=db_tractor, tractor_in=tractor_in)

@router.delete("/{tractor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tractor_listing_permanently(
    tractor_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Remove a tractor listing permanently from the database.
    Requires authentication. User must be the owner or an ADMIN.
    """
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id=tractor_id)
    if db_tractor is None:
        # If already deleted or never existed, still return 204 as per idempotent delete, or 404 by choice.
        # For this implementation, let's ensure it exists before trying to authorize/delete.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tractor not found")

    if db_tractor.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this tractor listing")

    deleted_tractor = tractor_service.delete_tractor(db=db, tractor_id=tractor_id)
    if not deleted_tractor : # Should not happen if previous check passed, but good for safety
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tractor not found during delete operation")
    return # Returns 204 No Content by default on success


@router.post("/{tractor_id}/upload-image/", response_model=TractorSchema)
async def upload_tractor_image_to_s3(
    tractor_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Upload an image for a tractor. The image URL will be added to the tractor's image_urls list.
    Requires authentication. User must be the owner of the tractor or an ADMIN.
    """
    db_tractor = tractor_service.get_tractor_by_id(db, tractor_id=tractor_id)
    if not db_tractor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tractor not found")

    # Authorization check
    if db_tractor.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to upload images for this tractor")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty. Please upload a valid image.")

    # The s3_service.upload_file_to_s3 function expects bytes or a file-like object.
    # `contents` is bytes here.
    image_url = await s3_service.upload_file_to_s3(contents, file.filename)

    if not image_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image.")

    # Ensure image_urls is a list. It should be initialized as default=[] in the model.
    if db_tractor.image_urls is None: # Should not happen with default=[]
        db_tractor.image_urls = []

    # Append new URL. This mutates the list if it's already a Python list.
    db_tractor.image_urls.append(image_url)

    # Mark the JSON field as modified for SQLAlchemy to detect the change.
    flag_modified(db_tractor, "image_urls")

    db.add(db_tractor) # Add to session to ensure changes are tracked
    db.commit()
    db.refresh(db_tractor)

    return db_tractor
