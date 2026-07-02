from fastapi import APIRouter, Depends, status
import aiosqlite
from src.auth.schemas import UserLoginSchema, TokenSchema
from src.auth import service as auth_service
from src.users import service as user_service
from src.auth.dependencies import get_current_user
from src.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login_user(
    user: UserLoginSchema,
    db: aiosqlite.Connection = Depends(get_db),
):
    authenticated_user = await auth_service.authenticate_user(
        user.email, user.password, db
    )
    payload_token = {
        "sub": str(authenticated_user["id"]),
        "token_version": authenticated_user.get("token_version", 0),
    }
    access_token = auth_service.create_access_token(payload_token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    current_user: dict = Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
):
    await user_service.invalidate_user_token(current_user["id"], db)
    return {"message": "User logged out successfully"}
