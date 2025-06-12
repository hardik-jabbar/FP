import random
import string
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..core.config import settings # For JWT secret, algorithm, expiry

# Password Hashing (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# OTP Generation and Hashing
def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of a given length."""
    if length <= 0:
        raise ValueError("OTP length must be positive")
    return "".join(random.choices(string.digits, k=length))

def get_otp_hash(otp: str) -> str:
    """Hashes an OTP using the same context as passwords for consistency."""
    # While bcrypt is strong, it might be slower than needed for OTPs.
    # For very high-traffic OTP systems, a faster hash like SHA256 might be considered,
    # but storing OTP hashes is better than plain text if they live for any duration.
    return pwd_context.hash(otp)

def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """Verifies a plain OTP against a hashed OTP."""
    return pwd_context.verify(plain_otp, hashed_otp)

# JWT Token Handling
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES if settings.ACCESS_TOKEN_EXPIRE_MINUTES else 30
        expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)}) # Add issued_at timestamp

    # Ensure SECRET_KEY and ALGORITHM are available from settings
    if not settings.SECRET_KEY or not settings.ALGORITHM:
        raise ValueError("JWT Secret Key or Algorithm not configured in settings.")

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Example decode function (will be part of dependencies.py usually)
# def decode_access_token(token: str) -> dict | None:
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         return payload
#     except JWTError:
#         return None
