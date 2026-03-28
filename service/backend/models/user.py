"""
User models for authentication and user management.
"""
from pydantic import BaseModel, field_validator
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: str
    name: str
    password: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: str
    password: str


class UserPublic(BaseModel):
    """Public user data (no password)."""
    id: str
    email: str
    name: str


class UserInDB(UserPublic):
    """User data as stored in the database (includes hashed password)."""
    password: str
