from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for user registration."""
    name: str = Field(..., min_length=2, max_length=255, description="Full name of the citizen/farmer")
    email: EmailStr = Field(..., description="Unique email address for login")
    password: str = Field(..., min_length=6, max_length=128, description="Plain text password (min 6 characters)")
    preferred_language: Optional[str] = Field(
        default="en", 
        pattern="^(en|hi|mr)$", 
        description="Preferred language code: 'en' (English), 'hi' (Hindi), 'mr' (Marathi)"
    )


class UserLoginRequest(BaseModel):
    """Schema for user authentication / login."""
    email: EmailStr = Field(..., description="User's registered email")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """Schema for returning user data (excluding password)."""
    id: int
    name: str
    email: str
    preferred_language: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for login/registration JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
