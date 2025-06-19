"""Authentication router that accepts JSON credentials and returns JWT.
Endpoint: POST /api/users/login
"""
from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi.util import get_remote_address  # For consistency if needed
from slowapi import Limiter, _rate_limit_exceeded_handler

from ..core.db import get_db
from ..schemas.user import Token, TokenData  # reuse existing Token
from ..schemas.user import LoginRequest
from ..services import user_service
from ..core.security import verify_password, create_access_token
from ..models.user import User as UserModel

# Re-use shared limiter instance from middleware to ensure global counters
try:
    from middleware.rate_limit import limiter as global_limiter  # type: ignore
except ImportError:
    global_limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/users", tags=["Auth (JSON)"])

# 20 requests per minute for unauthenticated login attempts
@router.post("/login", response_model=Token)
@global_limiter.limit("20/minute")
async def json_login(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Authenticate user via JSON body containing email and password."""
    user: UserModel | None = user_service.get_user_by_email(db, email=credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active or not user.is_verified:
        # Return 403 Forbidden for inactive/unverified accounts per spec
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive or unverified account. Please verify your email first.",
        )

    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    # Maintain same Token schema; expires_at could be derived client-side or extended if needed
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
