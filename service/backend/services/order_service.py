"""
Order service: creates and manages purchase orders.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from utils.file_handler import read_json, write_json, update_record
from services.cart_service import CartService

_cart_service = CartService()


class OrderService:
    """Handles order creation and status management. Persists to orders.json."""

    def create_order(
        self,
        user_id: str,
        shipping_address: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """
        Create a new order from the user's current cart.

        Raises:
            HTTPException 400: If the cart is empty.

        Returns:
            Newly created order dict with status 'pending'.
        """
        cart = _cart_service.get_cart(user_id)

        if not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create order: cart is empty"
            )

        order = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "items": [item.model_dump() for item in cart.items],
            "total": cart.total,
            "status": "pending",
            "payment_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "shipping_address": shipping_address or {},
            "tracking_number": None,
            "carrier": None,
            "tracking_events": [],
        }

        orders = read_json("orders.json")
        orders.append(order)
        write_json("orders.json", orders)

        return order

    def get_user_orders(self, user_id: str) -> List[dict]:
        """Return all orders for a given user, sorted newest first."""
        orders = read_json("orders.json")
        user_orders = [o for o in orders if o["user_id"] == user_id]
        return sorted(user_orders, key=lambda o: o["created_at"], reverse=True)

    def get_order_by_id(self, order_id: str, user_id: str) -> dict:
        """
        Retrieve a specific order for a user.

        Raises:
            HTTPException 404: If order doesn't exist or doesn't belong to user.
        """
        orders = read_json("orders.json")
        order = next(
            (o for o in orders if o["id"] == order_id and o["user_id"] == user_id),
            None
        )
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return order

    def update_status(
        self,
        order_id: str,
        new_status: str,
        payment_id: str | None = None
    ) -> dict:
        """
        Update an order's status and optionally set its payment_id.

        Args:
            order_id: ID of the order to update.
            new_status: New status string (e.g., 'paid', 'failed').
            payment_id: Transaction ID from the payment gateway.
        """
        updates = {"status": new_status}
        if payment_id:
            updates["payment_id"] = payment_id

        updated = update_record("orders.json", order_id, updates)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return updated

    def attach_tracking_after_payment(self, order_id: str) -> dict:
        """
        After successful payment, assign mock carrier + tracking number and timeline.
        Sets status to 'shipped' for demo purposes.
        """
        now = datetime.now(timezone.utc)
        tn = f"TRK-{uuid.uuid4().hex[:12].upper()}"
        events = [
            {
                "at": now.isoformat(),
                "description": "Pago confirmado — preparando envío",
                "location": "Almacén central",
            },
            {
                "at": (now + timedelta(hours=2)).isoformat(),
                "description": "Paquete recogido por transportista",
                "location": None,
            },
            {
                "at": (now + timedelta(days=1)).isoformat(),
                "description": "En tránsito hacia tu dirección",
                "location": "Red nacional",
            },
        ]
        updates = {
            "status": "shipped",
            "tracking_number": tn,
            "carrier": "ShopNow Express",
            "tracking_events": events,
        }
        updated = update_record("orders.json", order_id, updates)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        return updated

    def get_tracking(self, order_id: str, user_id: str) -> dict:
        """Return tracking slice for an order owned by the user."""
        order = self.get_order_by_id(order_id, user_id)
        return {
            "order_id": order["id"],
            "status": order.get("status"),
            "tracking_number": order.get("tracking_number"),
            "carrier": order.get("carrier"),
            "tracking_events": order.get("tracking_events") or [],
            "shipping_address": order.get("shipping_address") or {},
        }
