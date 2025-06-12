from sqlalchemy.orm import Session
from ..models.user import User, UserRole # Adjusted import
from ..schemas.user import UserCreate # UserUpdate might be needed for an update function later
from ..core.security import get_password_hash

def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieves a user by their email address.
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Creates a new user in the database.
    """
    hashed_password = get_password_hash(user.password)

    # For Pydantic V2, use model_dump()
    user_data = user.model_dump(exclude={"password"}) # Exclude password from dict

    db_user = User(
        **user_data,
        hashed_password=hashed_password,
        is_active=True, # Default, can be changed by admin or verification
        is_verified=False # Default, until email/OTP verification
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Retrieves a user by their ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User: # Changed UserCreate to UserUpdate
    """
    Updates a user's information in the database.
    """
    update_data = user_in.model_dump(exclude_unset=True) # Pydantic V2

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        db_user.hashed_password = hashed_password
        del update_data["password"] # Don't store plain password

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user) # Add to session, even if it's already there, to track changes
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> User | None:
    """
    Deletes a user from the database by their ID.
    Returns the deleted user object or None if not found.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def get_all_users(db: Session) -> list[User]:
    """
    Retrieves all users from thedatabase.
    """
    return db.query(User).all()

from datetime import datetime, timedelta, timezone # Added timezone
from ..core.security import generate_otp, get_otp_hash, verify_otp # Added verify_otp
# from ..core.config import settings # Uncomment if OTP expiry needs to be configurable via settings

# For now, OTP expiry is hardcoded, can be moved to settings if needed
OTP_EXPIRE_MINUTES = 15

def set_otp_for_user(db: Session, user: User) -> str:
    """
    Generates an OTP, stores its hash and expiry on the user record.
    Returns the plain OTP.
    """
    plain_otp = generate_otp()
    hashed_otp = get_otp_hash(plain_otp)

    user.otp_secret = hashed_otp
    user.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
    user.is_verified = False # Reset verification status when new OTP is set

    db.add(user)
    db.commit()
    db.refresh(user)
    return plain_otp

def verify_user_otp(db: Session, user: User, otp: str) -> bool:
    """
    Verifies the provided OTP for the user.
    If valid, marks user as verified and clears OTP fields.
    """
    if not user.otp_secret or not user.otp_expiry:
        return False # No OTP set for this user

    if datetime.now(timezone.utc) > user.otp_expiry:
        # OTP has expired, clear it
        user.otp_secret = None
        user.otp_expiry = None
        db.add(user)
        db.commit()
        return False

    if not verify_otp(otp, user.otp_secret):
        return False # Invalid OTP

    # OTP is valid and not expired
    user.is_verified = True
    user.otp_secret = None
    user.otp_expiry = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return True
