"""
Orders router: order history endpoints (requires authentication).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from services.order_service import OrderService
from utils.auth import decode_token

router = APIRouter()
_order_service = OrderService()

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


@router.get("/", summary="Get order history")
async def get_orders(user_id: str = Depends(get_current_user_id)):
    """
    Retrieve all orders for the authenticated user, sorted by date (newest first).
    """
    return _order_service.get_user_orders(user_id)


@router.get("/{order_id}/tracking", summary="Shipping tracking for an order")
async def get_order_tracking(
    order_id: str, user_id: str = Depends(get_current_user_id)
):
    """Return tracking number, carrier, and event timeline for the user's order."""
    return _order_service.get_tracking(order_id, user_id)


@router.get("/{order_id}", summary="Get order details")
async def get_order(order_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Retrieve a specific order by ID.

    Raises 404 if the order doesn't exist or doesn't belong to the current user.
    """
    return _order_service.get_order_by_id(order_id, user_id)
