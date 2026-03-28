"""
Order models for purchase tracking.
"""
from pydantic import BaseModel
from typing import List, Optional


class OrderItem(BaseModel):
    """Represents a product line in an order (snapshot at purchase time)."""
    product_id: str
    name: str
    price: float
    quantity: int


class Order(BaseModel):
    """Full order representation."""
    id: str
    user_id: str
    items: List[OrderItem]
    total: float
    status: str  # pending | paid | failed | shipped | cancelled
    payment_id: Optional[str] = None
    created_at: str


class OrderStatusUpdate(BaseModel):
    """Request body for updating order status."""
    status: str
    payment_id: Optional[str] = None
