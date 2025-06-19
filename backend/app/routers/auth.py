from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import Token, UserLogin
from app.services import auth as auth_service

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/users", tags=["auth"])
router.rate_limit_handler = _rate_limit_exceeded_handler


@router.post("/login", response_model=Token)
@limiter.limit("20/minute")
async def login(user_in: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, email=user_in.email, password=user_in.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(hours=auth_service.settings.jwt_expire_hours)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    expires_at = datetime.now(timezone.utc) + access_token_expires

    return Token(access_token=access_token, token_type="bearer", expires_at=expires_at)
