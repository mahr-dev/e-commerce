"""
Checkout router: orchestrates the order creation and payment flow.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.checkout import CheckoutRequest
from models.payment import PaymentRequest
from services.account_service import AccountService
from services.cart_service import CartService
from services.order_service import OrderService
from services.payment_service import PaymentService
from utils.auth import decode_token

router = APIRouter()
_cart_service = CartService()
_order_service = OrderService()
_payment_service = PaymentService()
_account_service = AccountService()

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


@router.post("", summary="Process checkout")
async def checkout(
    body: CheckoutRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Complete the checkout process:

    1. Create an order from the current cart (with shipping address)
    2. Process the payment via mock gateway
    3. Update the order status (paid / failed / pending)
    4. On success: attach mock tracking and clear the cart

    Dirección: `shipping_address` o `saved_address_id`.
    Pago: datos de tarjeta completos o `saved_payment_method_id` + `cvv` (simulación con PAN de prueba).
    """
    if body.saved_address_id:
        shipping = _account_service.get_shipping_payload_for_order(
            user_id, body.saved_address_id
        )
    else:
        shipping = body.shipping_address.model_dump()

    order = _order_service.create_order(user_id, shipping)

    if body.saved_payment_method_id:
        pm = _account_service.get_payment_method(user_id, body.saved_payment_method_id)
        holder = (body.card_holder or "").strip() or (
            pm.get("label") or f"{pm['brand']} •••• {pm['last4']}"
        )
        payment_data = PaymentRequest(
            order_id=order["id"],
            amount=order["total"],
            card_number="4242424242424242",
            card_holder=holder,
            expiry=pm["expiry"],
            cvv=body.cvv.strip(),
        )
    else:
        raw = body.card_number.replace(" ", "").replace("-", "")
        payment_data = PaymentRequest(
            order_id=order["id"],
            amount=order["total"],
            card_number=raw,
            card_holder=body.card_holder.strip(),
            expiry=body.expiry,
            cvv=body.cvv.strip(),
        )

    payment_result = _payment_service.process_payment(payment_data)

    if payment_result.status == "success":
        new_status = "paid"
    elif payment_result.status == "pending":
        new_status = "pending"
    else:
        new_status = "failed"

    updated_order = _order_service.update_status(
        order_id=order["id"],
        new_status=new_status,
        payment_id=payment_result.transaction_id,
    )

    if payment_result.success and payment_result.status == "success":
        updated_order = _order_service.attach_tracking_after_payment(order["id"])

    if payment_result.success:
        _cart_service.clear_cart(user_id)

    return {
        "order": updated_order,
        "payment": payment_result.model_dump(),
    }
