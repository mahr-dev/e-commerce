"""
Payment router: mock gateway, Stripe helpers (optional), and config status.
"""
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.payment import PaymentRequest, PaymentResponse
from models.stripe_checkout import StripeConfirmBody, StripePaymentIntentBody
from services.payment_service import PaymentService
from services.order_service import OrderService
from services.cart_service import CartService
from services.account_service import AccountService
from utils.auth import decode_token

router = APIRouter()
_payment_service = PaymentService()
_order_service = OrderService()
_cart_service = CartService()
_account_service = AccountService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"]


def _stripe_secret() -> str | None:
    key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    return key or None


def _stripe_publishable() -> str | None:
    key = os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip()
    return key or None


@router.get("/stripe/status", summary="Whether Stripe.js + PaymentIntents are available")
async def stripe_status():
    """
    Frontend can read `enabled` and `publishable_key` to show Stripe Elements.
    When `enabled` is false, use the mock card form at POST /checkout.
    """
    sec = _stripe_secret()
    return {
        "enabled": bool(sec),
        "publishable_key": _stripe_publishable() or "",
    }


@router.post("/stripe/payment-intent", summary="Create order + Stripe PaymentIntent")
async def create_stripe_payment_intent(
    body: StripePaymentIntentBody,
    user_id: str = Depends(get_current_user_id),
):
    """
    Creates a pending order from the cart and a PaymentIntent for Stripe.js.
    Confirm on the client with `stripe.confirmCardPayment`, then call POST /payment/stripe/confirm.
    """
    secret = _stripe_secret()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured (set STRIPE_SECRET_KEY).",
        )
    try:
        import stripe
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="stripe package is not installed.",
        ) from exc

    stripe.api_key = secret
    if body.saved_address_id:
        shipping = _account_service.get_shipping_payload_for_order(
            user_id, body.saved_address_id
        )
    else:
        shipping = body.shipping_address.model_dump()

    order = _order_service.create_order(user_id, shipping)
    amount_cents = int(round(float(order["total"]) * 100))
    if amount_cents < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order total too small for Stripe (minimum $0.50).",
        )

    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="usd",
        metadata={"order_id": order["id"], "user_id": user_id},
        automatic_payment_methods={"enabled": True},
    )

    return {
        "client_secret": intent.client_secret,
        "order_id": order["id"],
    }


@router.post("/stripe/confirm", summary="Finalize order after Stripe payment succeeds")
async def confirm_stripe_payment(
    body: StripeConfirmBody,
    user_id: str = Depends(get_current_user_id),
):
    """Verify PaymentIntent status and mark order paid, attach tracking, clear cart."""
    secret = _stripe_secret()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured.",
        )
    try:
        import stripe
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="stripe package is not installed.",
        ) from exc

    stripe.api_key = secret
    pi = stripe.PaymentIntent.retrieve(body.payment_intent_id)
    if pi.status != "succeeded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PaymentIntent not succeeded (status={pi.status}).",
        )

    meta = pi.metadata or {}
    order_id = meta.get("order_id")
    meta_user = meta.get("user_id")
    if not order_id or meta_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PaymentIntent does not match this session.",
        )

    order = _order_service.get_order_by_id(order_id, user_id)
    if order.get("status") not in ("pending",):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is not awaiting payment.",
        )

    _order_service.update_status(
        order_id=order_id,
        new_status="paid",
        payment_id=pi.id,
    )
    updated = _order_service.attach_tracking_after_payment(order_id)
    _cart_service.clear_cart(user_id)

    return {"order": updated, "payment_intent_id": pi.id}


@router.post("/process", response_model=PaymentResponse, summary="Process a payment")
async def process_payment(payment_request: PaymentRequest):
    """
    Process a payment through the mock gateway.

    **Test cards:**
    - `4242424242424242` → Always succeeds
    - `4000000000000002` → Always fails (card declined)
    - `4000000000000077` → Returns pending status
    - Any other valid card → 90% success rate

    Returns a PaymentResponse with status: success | failure | pending.
    """
    return _payment_service.process_payment(payment_request)
