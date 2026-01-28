"""
User Schemas
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field(
        default="operator",
        pattern="^(operator|security_lead|supervisor|admin)$"
    )


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(
        None,
        pattern="^(operator|security_lead|supervisor|admin)$"
    )
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class UserInDB(UserResponse):
    """Schema for user in database (includes hashed password)"""
    hashed_password: str


class Token(BaseModel):
    """OAuth2 token response"""
    access_token: str
    token_type: str = "bearer"


class TokenPair(Token):
    """Token pair with refresh token"""
    refresh_token: str


class TokenData(BaseModel):
    """Data extracted from token"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
