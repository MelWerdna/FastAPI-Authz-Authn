from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.database import get_db
from src.config import settings
import aiosqlite
import jwt


bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: aiosqlite.Connection = Depends(get_db),
):

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        token_version = payload.get("token_version")
    except (jwt.ExpiredSignatureError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    find_user = await cursor.fetchone()
    if not find_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    find_user = dict(find_user)
    if find_user.get("token_version", 0) != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated (user logged out)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return find_user


class UserRoleChecker:
    def __init__(self, required_role: str):
        self.required_role = required_role

    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") != self.required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required role to access this resource",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not current_user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is not active",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
