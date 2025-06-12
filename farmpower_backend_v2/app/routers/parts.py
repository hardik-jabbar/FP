from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified


from ..core.db import get_db
from ..core.dependencies import get_current_active_user
from ..models.user import User as UserModel, UserRole
from ..models.part import Part as PartModel # Renamed to avoid confusion
from ..schemas.part import PartSchema, PartCreate, PartUpdate
from ..services import part_service, s3_service # Import services

router = APIRouter(
    prefix="/parts",
    tags=["Tractor Parts Marketplace"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=PartSchema, status_code=status.HTTP_201_CREATED)
async def list_new_part_for_sale(
    part_in: PartCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    List a new tractor part for sale. Requires authentication.
    The seller_id will be automatically set to the current authenticated user.
    """
    return part_service.create_part(db=db, part_in=part_in, seller_id=current_user.id)

@router.get("/", response_model=List[PartSchema])
async def browse_all_parts_for_sale(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=200),
    category: Optional[str] = Query(None, description="Filter by part category (case-insensitive)"),
    tractor_brand: Optional[str] = Query(None, description="Filter by compatible tractor brand (case-insensitive partial match in list)"),
    condition: Optional[str] = Query(None, description="Filter by part condition (e.g., New, Used, Refurbished)"),
    min_price: Optional[float] = Query(None, alias="minPrice", gt=0),
    max_price: Optional[float] = Query(None, alias="maxPrice", gt=0),
    location: Optional[str] = Query(None, description="Filter by seller's location for the part"),
    seller_id: Optional[int] = Query(None, description="Filter by seller's user ID")
):
    """
    Browse available tractor parts. Open to public.
    Supports filtering by category, tractor brand compatibility, condition, price range, location, and seller.
    """
    if max_price is not None and min_price is not None and max_price < min_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="maxPrice cannot be less than minPrice.")

    parts = part_service.get_parts(
        db, skip=skip, limit=limit, category=category, tractor_brand=tractor_brand,
        condition=condition, min_price=min_price, max_price=max_price, location=location, seller_id=seller_id
    )
    return parts

@router.get("/{part_id}", response_model=PartSchema)
async def get_part_listing_details(
    part_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific part listing. Open to public.
    """
    db_part = part_service.get_part_by_id(db, part_id=part_id)
    if db_part is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")
    return db_part

@router.put("/{part_id}", response_model=PartSchema)
async def update_part_listing_details(
    part_id: int,
    part_in: PartUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update an existing part listing.
    Requires authentication. User must be the seller or an ADMIN.
    """
    db_part = part_service.get_part_by_id(db, part_id=part_id)
    if db_part is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")

    if db_part.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this part listing")

    return part_service.update_part(db=db, db_part=db_part, part_in=part_in)

@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_part_listing(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Remove a part listing.
    Requires authentication. User must be the seller or an ADMIN.
    """
    db_part = part_service.get_part_by_id(db, part_id=part_id)
    if db_part is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")

    if db_part.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this part listing")

    deleted_part = part_service.delete_part(db=db, part_id=part_id)
    if not deleted_part: # Should not happen if previous check passed
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found during delete operation")
    return

@router.post("/{part_id}/upload-image/", response_model=PartSchema)
async def upload_part_image(
    part_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Upload an image for a part. The image URL will be added to the part's image_urls list.
    Requires authentication. User must be the seller of the part or an ADMIN.
    """
    db_part = part_service.get_part_by_id(db, part_id=part_id)
    if not db_part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")

    if db_part.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to upload images for this part")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty.")

    image_url = await s3_service.upload_file_to_s3(contents, file.filename)

    if not image_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image.")

    if db_part.image_urls is None: # Should be initialized as default=[] in model
        db_part.image_urls = []

    db_part.image_urls.append(image_url)
    flag_modified(db_part, "image_urls") # Mark as modified for SQLAlchemy

    db.add(db_part)
    db.commit()
    db.refresh(db_part)

    return db_part
