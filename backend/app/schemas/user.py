from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class TokenData(BaseModel):
    email: EmailStr | None = None

class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=128)
