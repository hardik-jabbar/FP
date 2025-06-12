from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.db import get_db # To get DB session in get_current_user
from ..models.user import User as UserModel, UserRole # Import UserRole for RoleChecker
from ..services import user_service # To fetch user from DB
from ..schemas.user import TokenData # To validate token payload structure

# This URL must match the path of your token-issuing endpoint (login)
# If user router is prefixed with /users, then /users/login/token is correct.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        # Optional: Validate payload against TokenData schema
        # token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    # Optional: Add is_verified check here if needed for all authenticated routes
    # if not current_user.is_verified:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not verified")
    return current_user

# Role Checker Dependency Factory
def RoleChecker(allowed_roles: list[UserRole]):
    """
    Dependency factory that creates a dependency to check user roles.
    """
    async def role_dependency(
        current_user: UserModel = Depends(get_current_active_user)
    ) -> UserModel:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role.value}' is not authorized for this action. Allowed roles: {[role.value for role in allowed_roles]}.",
            )
        return current_user
    return role_dependency
