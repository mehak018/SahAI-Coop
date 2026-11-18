from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserRegisterRequest, 
    UserLoginRequest, 
    UserResponse, 
    TokenResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new citizen/farmer",
    description="Registers a new user, hashes their password with bcrypt, and returns an access token."
)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user:
    - **name**: Full name
    - **email**: Valid unique email
    - **password**: Password (min 6 characters)
    - **preferred_language**: Language code ('en', 'hi', or 'mr')
    """
    return AuthService.register_user(db=db, request=request)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticates the user with email and password and returns a JWT Bearer token."
)
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint:
    - **email**: Registered email address
    - **password**: User password
    """
    return AuthService.login_user(db=db, request=request)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns profile information for the authenticated user based on JWT Bearer token."
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return UserResponse.model_validate(current_user)
