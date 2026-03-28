"""
Stripe PaymentIntent flow (optional — requires STRIPE_SECRET_KEY).
"""
from typing import Optional

from pydantic import BaseModel, model_validator

from models.shipping import ShippingAddress


class StripePaymentIntentBody(BaseModel):
    """Create a PaymentIntent: shipping manual o dirección guardada."""
    shipping_address: Optional[ShippingAddress] = None
    saved_address_id: Optional[str] = None

    @model_validator(mode="after")
    def one_shipping(self):
        if bool(self.shipping_address) == bool(self.saved_address_id):
            raise ValueError(
                "Indica shipping_address o saved_address_id (exactamente uno)."
            )
        return self


class StripeConfirmBody(BaseModel):
    """Confirm server-side after client succeeds with Stripe.js."""
    payment_intent_id: str
