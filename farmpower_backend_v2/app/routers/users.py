from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..schemas.user import UserCreate, UserSchema, Token # Added Token schema
from ..models.user import User as UserModel, UserRole # Added UserRole
from ..core.security import verify_password, create_access_token # Removed get_password_hash (now in service)
from ..services import user_service # Import user_service
from fastapi.security import OAuth2PasswordRequestForm # For login form

router = APIRouter(
    prefix="/users", # Keep /users prefix for user-related actions like register, me, etc.
    tags=["Users"],
    responses={404: {"description": "Not found"}},
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


# Note: The tokenUrl for OAuth2PasswordBearer should match this endpoint's path
# If router prefix is /users, then tokenUrl="/users/login/token" is correct
@router.post("/login/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = user_service.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first."
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value} # Include role in token
    )
    return {"access_token": access_token, "token_type": "bearer"}


from ..core.dependencies import get_current_active_user, RoleChecker # Import dependencies
from ..schemas.user import UserUpdate # Import UserUpdate schema
from typing import List # For list response type

# --- User Management Endpoints (CRUD) ---

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    """
    Get current logged-in user's details.
    """
    return current_user

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
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's data")

@router.put("/{user_id}", response_model=UserSchema)
async def update_user_details(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update a user's details.
    Allowed for ADMIN or if the current_user is updating their own data.
    Note: Password updates should ideally be via a separate, more secure endpoint.
    """
    db_user = user_service.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.id == db_user.id or current_user.role == UserRole.ADMIN:
        # Admins can update more fields than regular users might be allowed to update for themselves.
        # This logic can be expanded in user_service.update_user if needed.
        updated_user = user_service.update_user(db=db, db_user=db_user, user_in=user_in)
        return updated_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user's data")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Delete a user by ID.
    Allowed for ADMIN or if the current_user is deleting their own account.
    """
    db_user_to_delete = user_service.get_user_by_id(db, user_id=user_id)
    if db_user_to_delete is None:
        # Still return 204 even if not found to avoid leaking info, or handle as 404 by choice
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return

    if current_user.id == db_user_to_delete.id or current_user.role == UserRole.ADMIN:
        user_service.delete_user(db=db, user_id=user_id)
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")


@router.get("/", response_model=List[UserSchema], dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def list_all_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
    # current_user is implicitly handled by RoleChecker for admin check
):
    """
    List all users. ADMIN access only.
    """
    users = user_service.get_all_users(db, skip=skip, limit=limit)
    return users


from ..schemas.user import OTPRequest, OTPVerify # Import OTP schemas

# --- OTP Verification Endpoints ---

@router.post("/request-verification-otp", status_code=status.HTTP_200_OK)
async def request_otp_for_verification(
    otp_request: OTPRequest,
    db: Session = Depends(get_db)
):
    """
    Request an OTP for email verification.
    """
    user = user_service.get_user_by_email(db, email=otp_request.email)
    if not user:
        # Generic message to prevent user enumeration
        return {"message": "If your email is registered, an OTP will be sent."}

    if user.is_verified:
        return {"message": "This account is already verified."}

    plain_otp = user_service.set_otp_for_user(db, user=user)

    # --- Mock Email Sending ---
    print(f"OTP for {user.email}: {plain_otp}")
    # TODO: Replace with actual email sending logic (e.g., using FastAPI-Mail or other library)
    # --- End Mock Email Sending ---

    return {"message": "An OTP has been sent to your email address for verification."}

@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_account_otp(
    otp_verify: OTPVerify,
    db: Session = Depends(get_db)
):
    """
    Verify OTP to activate/verify user account.
    """
    user = user_service.get_user_by_email(db, email=otp_verify.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or OTP not requested for this email.",
        )

    if user.is_verified:
         return {"message": "Account already verified."}

    if user_service.verify_user_otp(db, user=user, otp=otp_verify.otp):
        return {"message": "Email verified successfully. You can now login."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP. Please request a new one.",
        )
