from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse


class AuthService:
    """Service handling user registration, authentication, and JWT lifecycle."""

    @staticmethod
    def register_user(db: Session, request: UserRegisterRequest) -> TokenResponse:
        # Check if email is already registered
        existing_user = UserRepository.get_by_email(db, request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with email '{request.email}' already exists."
            )

        # Hash password securely using bcrypt
        hashed_pwd = hash_password(request.password)

        # Create new user record
        user = UserRepository.create(
            db=db,
            name=request.name,
            email=request.email,
            password_hash=hashed_pwd,
            preferred_language=request.preferred_language or "en"
        )

        # Generate JWT access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": "user"}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def login_user(db: Session, request: UserLoginRequest) -> TokenResponse:
        user = UserRepository.get_by_email(db, request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Verify password hash
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": "user"}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> UserResponse:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )
        return UserResponse.model_validate(user)
