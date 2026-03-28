"""
Authentication router: register and login endpoints.
"""
from fastapi import APIRouter

from models.user import UserCreate, UserLogin
from services.auth_service import AuthService

router = APIRouter()
_auth_service = AuthService()


@router.post("/register", summary="Register a new user")
async def register(user_data: UserCreate):
    """
    Create a new user account.

    - **email**: Valid email address (must be unique)
    - **name**: Display name
    - **password**: At least 6 characters

    Returns a JWT access token on success.
    """
    return _auth_service.register(user_data)


@router.post("/login", summary="Log in with email and password")
async def login(credentials: UserLogin):
    """
    Authenticate and receive a JWT access token.

    Returns user data and a Bearer token to use in subsequent requests.
    """
    return _auth_service.login(credentials)
