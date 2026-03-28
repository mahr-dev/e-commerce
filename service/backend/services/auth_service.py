"""
Authentication service: handles user registration and login.
"""
import uuid
from fastapi import HTTPException, status

from models.user import UserCreate, UserLogin, UserPublic
from utils.auth import hash_password, verify_password, create_access_token
from utils.file_handler import read_json, write_json


class AuthService:
    """
    Handles user registration and authentication.
    Persists users to users.json.
    """

    def register(self, user_data: UserCreate) -> dict:
        """
        Register a new user.

        Raises:
            HTTPException 400: If email is already in use.

        Returns:
            JWT access token + public user data.
        """
        users = read_json("users.json")

        # Ensure email uniqueness
        if any(u["email"] == user_data.email.lower() for u in users):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        new_user = {
            "id": str(uuid.uuid4()),
            "email": user_data.email.lower().strip(),
            "name": user_data.name.strip(),
            "password": hash_password(user_data.password),
            "phone": None,
            "addresses": [],
            "payment_methods": [],
        }

        users.append(new_user)
        write_json("users.json", users)

        token = create_access_token({"sub": new_user["id"], "email": new_user["email"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserPublic(
                id=new_user["id"],
                email=new_user["email"],
                name=new_user["name"]
            ).model_dump(),
        }

    def login(self, credentials: UserLogin) -> dict:
        """
        Authenticate a user with email and password.

        Raises:
            HTTPException 401: If credentials are invalid.

        Returns:
            JWT access token + public user data.
        """
        users = read_json("users.json")

        user = next(
            (u for u in users if u["email"] == credentials.email.lower().strip()),
            None
        )

        if not user or not verify_password(credentials.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token({"sub": user["id"], "email": user["email"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserPublic(
                id=user["id"],
                email=user["email"],
                name=user["name"]
            ).model_dump(),
        }
