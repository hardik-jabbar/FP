from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.db import get_db
from ..models import user as user_model # Using alias for clarity
from ..schemas import user as user_schema # Using alias for clarity
from ..services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> user_model.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        # We could also add token type validation here if needed (e.g., "access_token")
        # And check if "role" exists if we want to use it directly from token for some non-critical ops
    except JWTError:
        raise credentials_exception

    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: user_model.User = Depends(get_current_user)) -> user_model.User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def RoleChecker(allowed_roles: list[user_model.UserRole]):
    """
    Dependency that checks if the current user has one of the allowed roles.
    """
    def dependency(current_user: user_model.User = Depends(get_current_active_user)) -> user_model.User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions. User role not allowed."
            )
        return current_user
    return dependency

# Example of a role-based dependency (optional, can be expanded later)
# def get_current_admin_user(current_user: user_model.User = Depends(get_current_active_user)) -> user_model.User:
#     if current_user.role != user_model.UserRole.ADMIN:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="The user doesn't have enough privileges"
#         )
#     return current_user
