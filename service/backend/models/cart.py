"""
Cart models for shopping cart management.
"""
from pydantic import BaseModel
from typing import List, Optional


class CartItem(BaseModel):
    """Represents a single item in the cart."""
    product_id: str
    name: str
    price: float
    quantity: int
    image: Optional[str] = None

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


class Cart(BaseModel):
    """Represents the user's full shopping cart."""
    user_id: str
    items: List[CartItem] = []
    total: float = 0.0


class AddToCartRequest(BaseModel):
    """Request body for adding an item to the cart."""
    product_id: str
    quantity: int = 1

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod-001",
                "quantity": 2
            }
        }


class UpdateCartItemRequest(BaseModel):
    """Request body for updating item quantity in cart."""
    quantity: int


