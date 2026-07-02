from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
import aiosqlite
from fastapi import HTTPException, status
from src.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + delta
    payload.update({"exp": expire})
    jwt_token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return jwt_token


async def authenticate_user(
    email: str, password: str, db: aiosqlite.Connection
) -> dict:
    cursor = await db.execute(
        "SELECT * FROM users WHERE lower(email) = lower(?) AND is_deleted = 0",
        (email,),
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials: invalid email or deleted user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = dict(row)
    if not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials: invalid password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    await db.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user["id"],))
    await db.commit()
    user["is_active"] = 1
    return user
