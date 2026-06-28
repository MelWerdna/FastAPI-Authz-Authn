from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import ValidationError

from src.users.schemas import (
    AdminUserUpdateSchema,
    UserRegisterSchema,
    UserUpdateSchema,
    UserResponseSchema,
)
from src.users.schemas import UserRole
from src.users import service
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post(
    "/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserRegisterSchema):
    new_user = service.register_new_user(user)
    return new_user


@router.get("/me", response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get(
    "/{user_id}", response_model=UserResponseSchema, status_code=status.HTTP_200_OK
)
async def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    is_owner = current_user["id"] == user_id
    is_privileged = current_user.get("role") in [UserRole.ADMIN, UserRole.SUPERUSER]
    if not (is_owner or is_privileged):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this profile",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = service.get_user_by_id(user_id)
    return user


@router.patch(
    "/{user_id}", response_model=UserResponseSchema, status_code=status.HTTP_200_OK
)
async def update_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    payload: dict = Body(
        ..., example={"username": "new_username", "email": "new_email@example.com"}
    ),
):
    is_owner = current_user["id"] == user_id
    is_admin = current_user.get("role") == UserRole.ADMIN
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this profile",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        if is_admin:
            validate_data = AdminUserUpdateSchema(**payload)
        else:
            validate_data = UserUpdateSchema(**payload)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    update_data = validate_data.model_dump(exclude_unset=True)
    updated_user = service.update_user(user_id, update_data)
    return updated_user


@router.delete(
    "/{user_id}", response_model=UserResponseSchema, status_code=status.HTTP_200_OK
)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    is_owner = current_user["id"] == user_id
    is_admin = current_user.get("role") == UserRole.ADMIN
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this profile",
            headers={"WWW-Authenticate": "Bearer"},
        )
    deleted_user = service.delete_user(user_id)
    return deleted_user
