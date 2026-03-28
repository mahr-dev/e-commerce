"""
Authentication utilities: password hashing and JWT token management.

NOTE: This is a mock implementation for development/demo purposes.
In production, use bcrypt for password hashing and a secrets manager
for the SECRET_KEY.
"""
import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

# ⚠️  In production, load this from environment variables / secrets manager
SECRET_KEY = "ecommerce-super-secret-key-2024-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using SHA-256.
    In production, use bcrypt or argon2 instead.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain-text password against its stored hash."""
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JWT access token.

    Args:
        data: Payload to embed in the token (e.g., {"sub": user_id}).
        expires_delta: Custom expiry duration. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.

    Returns:
        Payload dict if valid, None if expired or invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
