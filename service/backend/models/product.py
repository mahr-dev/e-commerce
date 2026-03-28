"""
Product models for the eCommerce catalog.
"""
from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    """Full product representation."""
    id: str
    name: str
    description: str
    price: float
    image: str
    stock: int
    category: Optional[str] = None


class ProductSummary(BaseModel):
    """Lightweight product summary for list views."""
    id: str
    name: str
    price: float
    image: str
    stock: int
    category: Optional[str] = None
