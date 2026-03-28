"""
Combined checkout request: shipping + payment (mock gateway).

Either manual shipping_address or saved_address_id.
Either full card fields or saved_payment_method_id + cvv (mock uses test PAN server-side).
"""
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from models.shipping import ShippingAddress


class CheckoutRequest(BaseModel):
    """Client payload for POST /checkout (mock card processing)."""
    shipping_address: Optional[ShippingAddress] = None
    saved_address_id: Optional[str] = None

    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    expiry: Optional[str] = None
    cvv: Optional[str] = None
    saved_payment_method_id: Optional[str] = None

    @field_validator("card_number", "card_holder", "expiry", "cvv", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    @model_validator(mode="after")
    def validate_sources(self):
        if not self.saved_address_id and not self.shipping_address:
            raise ValueError("Indica una dirección manual o elige una guardada.")
        if self.saved_address_id and self.shipping_address:
            raise ValueError("Usa solo dirección nueva o solo dirección guardada, no ambas.")

        if self.saved_payment_method_id:
            if not self.cvv or not str(self.cvv).strip():
                raise ValueError("El CVV es obligatorio con tarjeta guardada.")
            if self.card_number or self.expiry:
                raise ValueError("No envíes número ni caducidad si usas tarjeta guardada.")
        else:
            if not all([self.card_number, self.card_holder, self.expiry, self.cvv]):
                raise ValueError(
                    "Para tarjeta nueva: número, titular, caducidad y CVV son obligatorios."
                )
        return self
