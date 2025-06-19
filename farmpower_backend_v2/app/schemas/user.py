from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Assuming UserRole is defined in app.models.user
# Adjust import path if your project structure is different or UserRole is elsewhere
from ..models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, example="John Doe")
    role: UserRole = Field(default=UserRole.FARMER) # Default role for creation if not specified

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel): # For PUT requests, all fields are optional
    full_name: Optional[str] = Field(None, example="Johnathan Doe")
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    # Password update should be handled via a separate endpoint or with specific logic
    # password: Optional[str] = Field(None, min_length=8)


# For responses, to avoid sending hashed_password, etc.
class UserSchema(UserBase):
    id: int
    is_active: bool
    is_banned: bool # Added is_banned
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Pydantic V2 (replaces orm_mode = True)

# --- Schemas for Token Handling ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# --- Schema for JSON Login ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    # You can add other fields to token data like user_id, roles if needed

# --- Schemas for OTP ---
class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=8) # Assuming OTP is typically 4-8 digits
