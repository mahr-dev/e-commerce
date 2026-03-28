"""
Cart router: shopping cart management (requires authentication).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.cart import AddToCartRequest, UpdateCartItemRequest
from services.cart_service import CartService
from utils.auth import decode_token

router = APIRouter()
_cart_service = CartService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Dependency: extract and validate user ID from JWT Bearer token."""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"]


@router.get("/", summary="Get current user's cart")
async def get_cart(user_id: str = Depends(get_current_user_id)):
    """Return the authenticated user's shopping cart."""
    return _cart_service.get_cart(user_id)


@router.post("/", summary="Add item to cart")
async def add_to_cart(
    request: AddToCartRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Add a product to the cart or increase its quantity if already present.

    Validates that requested quantity doesn't exceed available stock.
    """
    return _cart_service.add_item(user_id, request)


@router.put("/{product_id}", summary="Update item quantity")
async def update_cart_item(
    product_id: str,
    request: UpdateCartItemRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Set a specific quantity for a cart item.
    Setting quantity to 0 removes the item.
    """
    return _cart_service.update_quantity(user_id, product_id, request.quantity)


@router.delete("/{product_id}", summary="Remove item from cart")
async def remove_from_cart(
    product_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Remove a specific product from the cart."""
    return _cart_service.remove_item(user_id, product_id)


@router.delete("/", summary="Clear entire cart")
async def clear_cart(user_id: str = Depends(get_current_user_id)):
    """Remove all items from the cart."""
    _cart_service.clear_cart(user_id)
    return {"message": "Cart cleared successfully"}
