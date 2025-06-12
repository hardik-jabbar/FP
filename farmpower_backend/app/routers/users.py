from fastapi import APIRouter, Depends, HTTPException, status # Added status
from pydantic import BaseModel, EmailStr # Added for OTP request models
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..schemas.user import User, UserCreate
from ..models.user import User as UserModel # UserModel is still needed for the /login endpoint's query
from ..core.security import verify_password, create_access_token # get_password_hash is now in user_service
from fastapi.security import OAuth2PasswordRequestForm
from ..services import user_service # Import the user service

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Placeholder comment removed or adjusted as necessary

@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists using the service
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user using the service
    return user_service.create_user(db=db, user=user)

@router.post("/login/token") # Or just /login, but /login/token is common for OAuth2
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401, # Corrected status code for unauthorized
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        # Optionally, you could allow login but restrict access via dependencies,
        # or re-trigger OTP here. Forcing verification before login is simplest for now.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # 403 Forbidden is appropriate
            detail="Email not verified. Please verify your email first."
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value} # Added role to token
    )
    return {"access_token": access_token, "token_type": "bearer"}

from ..core.dependencies import get_current_active_user # Import the dependency
from ..schemas.user import UserUpdate # Import UserUpdate for the update endpoint

# Placeholder endpoints for future implementation

@router.get("/{user_id}", response_model=User)
async def read_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user) # Secure the endpoint
):
    # Fetch user by ID using the service
    user = user_service.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Authorization: For now, any authenticated user can view any profile.
    # More specific checks (e.g., if current_user.id == user_id or current_user.role == ADMIN)
    # can be added here or in the service layer if needed.
    return user

@router.put("/{user_id}", response_model=User)
async def update_user_profile(
    user_id: int,
    user_update: UserUpdate, # Use UserUpdate schema for input
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user) # Secure the endpoint
):
    db_user_to_update = user_service.get_user_by_id(db, user_id=user_id)
    if not db_user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    # Authorization check
    if current_user.id != db_user_to_update.id and current_user.role != UserModel.role.ADMIN: # Assuming UserRole is on UserModel
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    updated_user = user_service.update_user(db=db, db_user=db_user_to_update, user_in=user_update)
    return updated_user

@router.delete("/{user_id}", status_code=204) # 204 No Content for successful deletion
async def delete_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user) # Secure the endpoint
):
    db_user_to_delete = user_service.get_user_by_id(db, user_id=user_id)
    if not db_user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    # Authorization check
    if current_user.id != db_user_to_delete.id and current_user.role != UserModel.role.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    user_service.delete_user(db=db, user_id=user_id)
    return # For 204 No Content, we return nothing

from ..models.user import UserRole # Import UserRole for RoleChecker
from ..core.dependencies import RoleChecker # Import RoleChecker
from typing import List # For list response type

@router.get("/", response_model=List[User]) # Add new endpoint to list all users
async def list_all_users(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(RoleChecker([UserRole.ADMIN])) # Secure with ADMIN role
):
    """
    Retrieves a list of all users. Only accessible by ADMIN users.
    """
    users = user_service.get_all_users(db=db)
    return users

# --- OTP Verification Endpoint Stubs ---

class OTPRequest(BaseModel): # Pydantic model for request body
    email: EmailStr

class OTPVerify(BaseModel): # Pydantic model for request body
    email: EmailStr
    otp: str

@router.post("/request-verification-otp", status_code=status.HTTP_200_OK)
async def request_verification_otp(
    otp_request: OTPRequest, # Use Pydantic model for request body
    db: Session = Depends(get_db)
):
    # TODO:
    # 1. Fetch user by otp_request.email using user_service.get_user_by_email.
    # 2. If user exists and not user.is_verified:
    #    a. Generate OTP (e.g., 6 random digits).
    #    b. Hash the OTP. Store user.otp_secret = hashed_otp.
    #    c. Set user.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10) (for example).
    #    d. Save user object.
    #    e. Send OTP to user's email (requires email library and configuration - out of scope for now).
    # 3. Return a generic success message to avoid leaking info about user existence/status.
    #    (e.g., "If a user with this email exists and is not verified, an OTP will be sent.")
    # For now, just a placeholder:
    # user = user_service.get_user_by_email(db, email=otp_request.email)
    user = user_service.get_user_by_email(db, email=otp_request.email)

    if not user:
        # To prevent user enumeration, we can return a generic message even if user doesn't exist.
        # However, for testing/debugging, you might want to know if user was found.
        # For production, a generic message is safer.
        # raise HTTPException(status_code=404, detail="User not found")
        return {"message": "If your email is registered and not verified, an OTP will be sent."}

    if user.is_verified:
        return {"message": "User already verified."}

    plain_otp = user_service.set_otp_for_user(db, user)

    # --- Mock Email Sending ---
    print(f"OTP for {user.email}: {plain_otp}")
    # In a real app, replace print with: await send_otp_email(user.email, plain_otp)
    # --- End Mock Email Sending ---

    return {"message": "OTP has been sent to your email address."}


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(
    otp_verify: OTPVerify, # Use Pydantic model for request body
    db: Session = Depends(get_db)
):
    # TODO:
    # 1. Fetch user by otp_verify.email.
    # 2. If user exists and user.otp_secret and user.otp_expiry are set:
    #    a. Check if datetime.now(timezone.utc) > user.otp_expiry. If so, OTP expired.
    #    b. Verify provided otp_verify.otp against user.otp_secret (requires hashing the input OTP).
    #    c. If valid and not expired:
    #       i. Set user.is_verified = True.
    #       ii. Clear user.otp_secret and user.otp_expiry.
    #       iii. Save user object.
    #       iv. Return success message.
    #    d. Else, return error (invalid OTP or expired).
    # 3. Else (user not found or OTP not set), return error.
    # For now, just a placeholder:
    # user = user_service.get_user_by_email(db, email=otp_verify.email)
    user = user_service.get_user_by_email(db, email=otp_verify.email)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or OTP request not initiated.")

    if user.is_verified: # Check if already verified
        return {"message": "User already verified."}

    success = user_service.verify_user_otp(db, user, otp_verify.otp)

    if success:
        return {"message": "Email verified successfully."}
    else:
        # Consider more specific error messages for debugging if needed,
        # but for client, "Invalid or expired OTP" is usually sufficient.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP.")
