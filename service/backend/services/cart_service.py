"""
Cart service: in-memory shopping cart management per user.

Note: Carts are stored in memory. They reset when the server restarts.
In production, use Redis or a persistent store.
"""
from typing import Dict
from fastapi import HTTPException, status

from models.cart import Cart, CartItem, AddToCartRequest
from services.product_service import ProductService

# In-memory store: { user_id: Cart }
_carts: Dict[str, Cart] = {}

_product_service = ProductService()


class CartService:
    """Manages per-user shopping carts stored in memory."""

    def get_cart(self, user_id: str) -> Cart:
        """Return the user's cart, creating an empty one if it doesn't exist."""
        if user_id not in _carts:
            _carts[user_id] = Cart(user_id=user_id)
        return _carts[user_id]

    def add_item(self, user_id: str, request: AddToCartRequest) -> Cart:
        """
        Add a product to the cart or increment its quantity.

        Raises:
            HTTPException 400: If requested quantity exceeds available stock.
        """
        product = _product_service.get_by_id(request.product_id)

        if product["stock"] < request.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product['stock']} units available in stock"
            )

        cart = self.get_cart(user_id)

        existing = next(
            (item for item in cart.items if item.product_id == request.product_id),
            None
        )

        if existing:
            # Ensure total quantity doesn't exceed stock
            new_qty = existing.quantity + request.quantity
            if new_qty > product["stock"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot add {request.quantity} more. Only {product['stock'] - existing.quantity} units left"
                )
            existing.quantity = new_qty
        else:
            cart.items.append(CartItem(
                product_id=product["id"],
                name=product["name"],
                price=product["price"],
                quantity=request.quantity,
                image=product.get("image"),
            ))

        cart.total = round(
            sum(item.price * item.quantity for item in cart.items), 2
        )
        _carts[user_id] = cart
        return cart

    def remove_item(self, user_id: str, product_id: str) -> Cart:
        """Remove a product entirely from the cart."""
        cart = self.get_cart(user_id)
        cart.items = [i for i in cart.items if i.product_id != product_id]
        cart.total = round(
            sum(item.price * item.quantity for item in cart.items), 2
        )
        _carts[user_id] = cart
        return cart

    def update_quantity(self, user_id: str, product_id: str, quantity: int) -> Cart:
        """
        Update the quantity of a specific cart item.

        If quantity is 0 or less, the item is removed.
        """
        if quantity <= 0:
            return self.remove_item(user_id, product_id)

        product = _product_service.get_by_id(product_id)
        if quantity > product["stock"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product['stock']} units available"
            )

        cart = self.get_cart(user_id)
        item = next((i for i in cart.items if i.product_id == product_id), None)
        if item:
            item.quantity = quantity
        cart.total = round(
            sum(i.price * i.quantity for i in cart.items), 2
        )
        _carts[user_id] = cart
        return cart

    def clear_cart(self, user_id: str) -> None:
        """Empty the user's cart (called after successful checkout)."""
        _carts[user_id] = Cart(user_id=user_id)
