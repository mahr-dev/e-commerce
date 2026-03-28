"""
Payment models for the mock payment gateway.
Simulates a Stripe-like payment processing flow.
"""
from pydantic import BaseModel
from typing import Optional


class PaymentRequest(BaseModel):
    """
    Payment request payload.

    Test cards:
    - 4000000000000002 → Always fails (card declined)
    - 4000000000000077 → Always results in pending
    - Any other 16-digit number → 90% success rate
    """
    order_id: str
    amount: float
    card_number: str
    card_holder: str
    expiry: str   # MM/YY format
    cvv: str

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ord-xxx",
                "amount": 149.99,
                "card_number": "4242424242424242",
                "card_holder": "John Doe",
                "expiry": "12/26",
                "cvv": "123"
            }
        }


class PaymentResponse(BaseModel):
    """Payment gateway response."""
    success: bool
    transaction_id: Optional[str] = None
    status: str            # success | failure | pending
    message: str
