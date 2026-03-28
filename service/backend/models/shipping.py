"""
Shipping address and tracking payloads.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ShippingAddress(BaseModel):
    """Physical delivery address."""
    full_name: str = Field(..., min_length=2, max_length=120)
    line1: str = Field(..., min_length=3, max_length=200)
    line2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=3, max_length=20)
    country: str = Field(default="ES", min_length=2, max_length=2)
    phone: Optional[str] = Field(None, max_length=40)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TrackingEvent(BaseModel):
    """Single tracking checkpoint."""
    at: str
    description: str
    location: Optional[str] = None
