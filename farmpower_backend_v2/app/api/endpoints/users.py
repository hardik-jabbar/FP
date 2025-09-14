from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from ...core.db import get_db
from ...core.dependencies import get_current_active_user, RoleChecker
from ...models.user import User as UserModel, UserRole
from ...schemas.user import (
    UserCreate, UserUpdate, UserSchema, Token, 
    TokenData, LoginRequest, OTPRequest, OTPVerify
)
from ...services import user_service
from ...core.security import verify_password, create_access_token

router = APIRouter(
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    db_user_found = user_service.get_user_by_email(db, email=user.email)
    if db_user_found:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    created_user = user_service.create_user(db=db, user_in=user)
    return created_user

@router.post("/login/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active and not banned
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account banned. Please contact support.",
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    """
    Get current logged-in user's details.
    """
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update own user details.
    """
    updated_user = user_service.update_user(db, current_user.id, user_in)
    return updated_user

@router.get("/{user_id}", response_model=UserSchema)
async def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get any user's details by ID.
    Allowed for ADMIN or if the current_user is requesting their own data.
    """
    if current_user.id == user_id or current_user.role == UserRole.ADMIN:
        user = user_service.get_user_by_id(db, user_id=user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Not authorized to access this user's data"
    )

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update a user's details.
    Admin can update any user, users can only update their own data.
    """
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )
        
    db_user = user_service.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = user_service.update_user(db, user_id=user_id, user_update=user_update)
    return updated_user

@router.get("/", response_model=List[UserSchema], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def list_all_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all users. ADMIN access only.
    """
    users = user_service.get_all_users(db, skip=skip, limit=limit)
    return users

@router.post("/request-otp", response_model=dict)
async def request_otp(
    otp_request: OTPRequest,
    db: Session = Depends(get_db)
):
    """
    Request OTP for user verification.
    """
    user = user_service.get_user_by_email(db, email=otp_request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    success = user_service.send_otp(db, user_id=user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )

    return {"message": "OTP sent successfully"}

@router.post("/verify-otp", response_model=UserSchema)
async def verify_otp(
    otp_verify: OTPVerify,
    db: Session = Depends(get_db)
):
    """
    Verify OTP for user verification.
    """
    user = user_service.get_user_by_email(db, email=otp_verify.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already verified"
        )

    verification_success = user_service.verify_otp(
        db, 
        user_id=user.id, 
        otp=otp_verify.otp
    )
    
    if not verification_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    return user