from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from ..models.user import User as UserModel, UserRole
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, generate_otp, get_otp_hash, verify_otp
# from ..core.config import settings # If OTP_EXPIRE_MINUTES needs to be configurable

# For now, OTP expiry is hardcoded, can be moved to settings if needed
OTP_EXPIRE_MINUTES = 15

class UserService:
    def get_user_by_email(self, db: Session, email: str) -> Optional[UserModel]:
        return db.query(UserModel).filter(UserModel.email == email).first()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[UserModel]:
        return db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_all_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
        return db.query(UserModel).offset(skip).limit(limit).all()

    def create_user(self, db: Session, user_in: UserCreate) -> UserModel:
        hashed_password = get_password_hash(user_in.password)

        # Create user instance
        db_user = UserModel(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role, # Role from UserCreate, which has a default
            is_active=True,   # Default to active
            is_verified=False # Default to not verified
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update_user(self, db: Session, db_user: UserModel, user_in: UserUpdate) -> UserModel:
        update_data = user_in.model_dump(exclude_unset=True) # Pydantic V2

        if "password" in update_data and update_data["password"]: # If password is being updated
            hashed_password = get_password_hash(update_data["password"])
            db_user.hashed_password = hashed_password
            del update_data["password"] # Don't store plain password directly

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.add(db_user) # Add to session to track changes
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete_user(self, db: Session, user_id: int) -> Optional[UserModel]:
        db_user = self.get_user_by_id(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()
        return db_user # Returns the deleted user or None

    # --- OTP Specific Methods ---
    def set_otp_for_user(self, db: Session, user: UserModel) -> str:
        """
        Generates an OTP, stores its hash and expiry on the user record.
        Returns the plain OTP.
        """
        plain_otp = generate_otp()
        hashed_otp = get_otp_hash(plain_otp) # Use the new get_otp_hash

        user.otp_secret = hashed_otp
        user.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
        user.is_verified = False # Reset verification status when new OTP is set

        db.add(user)
        db.commit()
        db.refresh(user)
        return plain_otp

    def verify_user_otp(self, db: Session, user: UserModel, otp: str) -> bool:
        """
        Verifies the provided OTP for the user.
        If valid, marks user as verified and clears OTP fields.
        """
        if not user.otp_secret or not user.otp_expiry:
            return False # No OTP set for this user

        if datetime.now(timezone.utc) > user.otp_expiry:
            # OTP has expired, clear it for security
            user.otp_secret = None
            user.otp_expiry = None
            db.add(user)
            db.commit()
            return False

        if not verify_otp(otp, user.otp_secret): # Use the new verify_otp
            return False # Invalid OTP

        # OTP is valid and not expired
        user.is_verified = True
        user.otp_secret = None
        user.otp_expiry = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return True

user_service = UserService() # Create an instance of the service
