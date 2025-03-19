from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, HttpUrl, constr

from app.schemas.token import Token as TokenSchema


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    is_admin: bool = False
    avatar_url: Optional[HttpUrl] = None
    xrpl_address: Optional[str] = None
    is_nonprofit: bool = False


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: constr(min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    avatar_url: Optional[HttpUrl] = None
    xrpl_address: Optional[str] = None


class UserInDB(UserBase):
    """User schema with hashed password."""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserBase):
    """Complete user schema without sensitive data."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDBBase(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    tokens: Optional[List[TokenSchema]] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None 