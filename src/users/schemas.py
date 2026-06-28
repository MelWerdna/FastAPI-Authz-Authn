from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class UserRegisterSchema(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    password_retype: str = Field(..., min_length=8, description="Retype user password")
    username: str = Field(..., min_length=3, max_length=15, description="User username")


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(
        None, min_length=3, max_length=15, description="User username"
    )


class AdminUserUpdateSchema(UserUpdateSchema):
    is_deleted: Optional[bool] = Field(
        None, description="Indicates if the user is deleted"
    )
    role: Optional[UserRole] = Field(None, description="User role")


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: UserRole
    is_deleted: bool

    model_config = {"from_attributes": True}
