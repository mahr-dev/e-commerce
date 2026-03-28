"""
User profile: personal info, saved addresses, payment method references (mock).
"""
import uuid
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from models.account import AddressCreate, PaymentMethodCreate, ProfileUpdate
from utils.file_handler import read_json, write_json


def _ensure_user_shape(user: Dict[str, Any]) -> None:
    if "phone" not in user:
        user["phone"] = None
    if "addresses" not in user or user["addresses"] is None:
        user["addresses"] = []
    if "payment_methods" not in user or user["payment_methods"] is None:
        user["payment_methods"] = []


class AccountService:
    """CRUD on users.json for profile fields (no password here)."""

    def _find_user_index(self, user_id: str) -> int:
        users = read_json("users.json")
        for i, u in enumerate(users):
            if u.get("id") == user_id:
                return i
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    def get_shipping_payload_for_order(self, user_id: str, address_id: str) -> Dict[str, Any]:
        """Shipping dict for order creation from a saved address."""
        prof = self.get_profile(user_id)
        for a in prof["addresses"]:
            if a.get("id") == address_id:
                return {
                    "full_name": a["full_name"],
                    "line1": a["line1"],
                    "line2": a.get("line2"),
                    "city": a["city"],
                    "state": a["state"],
                    "postal_code": a["postal_code"],
                    "country": a["country"],
                    "phone": a.get("phone"),
                    "latitude": a.get("latitude"),
                    "longitude": a.get("longitude"),
                }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    def get_payment_method(self, user_id: str, pm_id: str) -> dict:
        """Single saved payment method or 404."""
        prof = self.get_profile(user_id)
        for p in prof["payment_methods"]:
            if p.get("id") == pm_id:
                return p
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found",
        )

    def get_profile(self, user_id: str) -> dict:
        users = read_json("users.json")
        user = next((u for u in users if u.get("id") == user_id), None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        _ensure_user_shape(user)
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "phone": user.get("phone"),
            "addresses": list(user.get("addresses") or []),
            "payment_methods": list(user.get("payment_methods") or []),
        }

    def update_profile(self, user_id: str, data: ProfileUpdate) -> dict:
        if data.name is None and data.phone is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )
        users = read_json("users.json")
        idx = self._find_user_index(user_id)
        user = users[idx]
        _ensure_user_shape(user)

        if data.name is not None:
            user["name"] = data.name.strip()
        if data.phone is not None:
            p = data.phone.strip()
            user["phone"] = p if p else None

        users[idx] = user
        write_json("users.json", users)
        return self.get_profile(user_id)

    def add_address(self, user_id: str, body: AddressCreate) -> dict:
        users = read_json("users.json")
        idx = self._find_user_index(user_id)
        user = users[idx]
        _ensure_user_shape(user)

        addr = body.model_dump()
        addr["id"] = str(uuid.uuid4())
        if body.is_default:
            for a in user["addresses"]:
                a["is_default"] = False
        user["addresses"].append(addr)

        users[idx] = user
        write_json("users.json", users)
        return addr

    def update_address(self, user_id: str, address_id: str, body: AddressCreate) -> dict:
        users = read_json("users.json")
        idx = self._find_user_index(user_id)
        user = users[idx]
        _ensure_user_shape(user)

        found = None
        for a in user["addresses"]:
            if a.get("id") == address_id:
                found = a
                break
        if not found:
            raise HTTPException(status_code=404, detail="Address not found")

        new_data = body.model_dump()
        new_data["id"] = address_id
        if body.is_default:
            for a in user["addresses"]:
                a["is_default"] = False

        i = user["addresses"].index(found)
        user["addresses"][i] = new_data

        users[idx] = user
        write_json("users.json", users)
        return new_data

    def delete_address(self, user_id: str, address_id: str) -> None:
        users = read_json("users.json")
        idx = self._find_user_index(user_id)
        user = users[idx]
        _ensure_user_shape(user)

        before = len(user["addresses"])
        user["addresses"] = [a for a in user["addresses"] if a.get("id") != address_id]
        if len(user["addresses"]) == before:
            raise HTTPException(status_code=404, detail="Address not found")

        users[idx] = user
        write_json("users.json", users)

    def add_payment_method(self, user_id: str, body: PaymentMethodCreate) -> dict:
        users = read_json("users.json")
        idx = self._find_user_index(user_id)
        user = users[idx]
        _ensure_user_shape(user)

        pm = {
            "id": str(uuid.uuid4()),
            "brand": body.brand.strip(),
            "last4": body.last4,
            "expiry": body.expiry,
            "label": (body.label or "").strip() or None,
            "is_default": body.is_default,
        }
        if body.is_default:
            for p in user["payment_methods"]:
                p["is_default"] = False
        user["payment_methods"].append(pm)

        users[idx] = user
        write_json("users.json", users)
        return pm

    def delete_payment_method(self, user_id: str, pm_id: str) -> None:
        users = read_json("users.json")
        idx = self._find_user_index(user_id)
        user = users[idx]
        _ensure_user_shape(user)

        before = len(user["payment_methods"])
        user["payment_methods"] = [p for p in user["payment_methods"] if p.get("id") != pm_id]
        if len(user["payment_methods"]) == before:
            raise HTTPException(status_code=404, detail="Payment method not found")

        users[idx] = user
        write_json("users.json", users)

    def set_default_payment_method(self, user_id: str, pm_id: str) -> dict:
        users = read_json("users.json")
        idx = self._find_user_index(user_id)
        user = users[idx]
        _ensure_user_shape(user)

        ok = False
        for p in user["payment_methods"]:
            if p.get("id") == pm_id:
                p["is_default"] = True
                ok = True
            else:
                p["is_default"] = False
        if not ok:
            raise HTTPException(status_code=404, detail="Payment method not found")

        users[idx] = user
        write_json("users.json", users)
        return self.get_profile(user_id)
