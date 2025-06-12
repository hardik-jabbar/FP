from pydantic import BaseModel, EmailStr
from typing import Optional

# Import UserRole from the models directory
# Assuming models is a sibling directory to schemas within an 'app' package
from ..models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class User(UserBase): # For response model
    id: int
    is_active: bool
    is_verified: bool

    class Config:
        # This is Pydantic V1 style. For V2, it's `from_attributes = True`
        orm_mode = True # Tells Pydantic to read the data even if it is not a dict, but an ORM model (or any other arbitrary object with attributes)

# If using Pydantic V2, replace orm_mode = True with from_attributes = True
# For example:
# class User(UserBase):
#     id: int
#     is_active: bool
#     is_verified: bool
#
#     class Config:
#         from_attributes = True
