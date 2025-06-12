from passlib.context import CryptContext

# For new hashes, bcrypt will be used.
# For verifying existing hashes, it will automatically detect and handle older schemes if present.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

from datetime import datetime, timedelta, timezone
from jose import jwt
from ..core.config import settings

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

import random
import string

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of a given length."""
    if length <= 0:
        raise ValueError("OTP length must be positive")
    return "".join(random.choices(string.digits, k=length))

def get_otp_hash(otp: str) -> str:
    """Hashes an OTP using the same context as passwords."""
    return pwd_context.hash(otp)

def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """Verifies a plain OTP against a hashed OTP."""
    return pwd_context.verify(plain_otp, hashed_otp)
