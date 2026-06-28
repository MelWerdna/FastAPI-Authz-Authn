from pydantic import BaseModel, EmailStr, Field


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class TokenSchema(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = "bearer"
