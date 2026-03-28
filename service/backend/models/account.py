"""
Account / profile models (addresses & payment methods stored on user record).
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ProfileUpdate(BaseModel):
    """Update display name and phone."""
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    phone: Optional[str] = Field(None, max_length=40)


class Address(BaseModel):
    """Saved shipping address."""
    id: str
    label: str = Field(..., min_length=1, max_length=60)
    full_name: str = Field(..., min_length=2, max_length=120)
    line1: str = Field(..., min_length=3, max_length=200)
    line2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=3, max_length=20)
    country: str = Field(default="ES", min_length=2, max_length=2)
    phone: Optional[str] = Field(None, max_length=40)
    is_default: bool = False


class AddressCreate(BaseModel):
    """Create address (id assigned server-side)."""
    label: str = Field(..., min_length=1, max_length=60)
    full_name: str = Field(..., min_length=2, max_length=120)
    line1: str = Field(..., min_length=3, max_length=200)
    line2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=3, max_length=20)
    country: str = Field(default="ES", min_length=2, max_length=2)
    phone: Optional[str] = Field(None, max_length=40)
    is_default: bool = False


class PaymentMethod(BaseModel):
    """Stored payment method (mock — never full PAN)."""
    id: str
    brand: str = Field(..., min_length=2, max_length=32)
    last4: str = Field(..., min_length=4, max_length=4)
    expiry: str = Field(..., pattern=r"^\d{2}/\d{2}$")
    label: Optional[str] = Field(None, max_length=80)
    is_default: bool = False


class PaymentMethodCreate(BaseModel):
    """Add a mock card reference for display at checkout."""
    brand: str = Field(..., min_length=2, max_length=32)
    last4: str = Field(..., min_length=4, max_length=4)
    expiry: str = Field(..., pattern=r"^\d{2}/\d{2}$")
    label: Optional[str] = Field(None, max_length=80)
    is_default: bool = False

    @field_validator("last4")
    @classmethod
    def last4_digits(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 4:
            raise ValueError("last4 must be exactly 4 digits")
        return v
