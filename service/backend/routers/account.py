"""
Account settings: profile, addresses, payment methods (authenticated).
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer

from models.account import AddressCreate, PaymentMethodCreate, ProfileUpdate
from services.account_service import AccountService
from utils.auth import decode_token

router = APIRouter()
_account = AccountService()

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


@router.get("/me", summary="Current user profile")
async def get_me(user_id: str = Depends(get_current_user_id)):
    """Name, email, phone, saved addresses and payment method references."""
    return _account.get_profile(user_id)


@router.patch("/me", summary="Update profile")
async def patch_me(body: ProfileUpdate, user_id: str = Depends(get_current_user_id)):
    """Update name and/or phone."""
    return _account.update_profile(user_id, body)


@router.post("/addresses", summary="Add address")
async def add_address(body: AddressCreate, user_id: str = Depends(get_current_user_id)):
    return _account.add_address(user_id, body)


@router.patch("/addresses/{address_id}", summary="Update address")
async def update_address(
    address_id: str,
    body: AddressCreate,
    user_id: str = Depends(get_current_user_id),
):
    return _account.update_address(user_id, address_id, body)


@router.delete("/addresses/{address_id}", summary="Delete address", status_code=204)
async def delete_address(address_id: str, user_id: str = Depends(get_current_user_id)):
    _account.delete_address(user_id, address_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/payment-methods", summary="Add payment method (mock)")
async def add_pm(body: PaymentMethodCreate, user_id: str = Depends(get_current_user_id)):
    return _account.add_payment_method(user_id, body)


@router.delete("/payment-methods/{pm_id}", summary="Remove payment method", status_code=204)
async def delete_pm(pm_id: str, user_id: str = Depends(get_current_user_id)):
    _account.delete_payment_method(user_id, pm_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/payment-methods/{pm_id}/default",
    summary="Set default payment method",
)
async def default_pm(pm_id: str, user_id: str = Depends(get_current_user_id)):
    return _account.set_default_payment_method(user_id, pm_id)
