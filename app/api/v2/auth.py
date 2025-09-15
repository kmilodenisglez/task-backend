"""
Enhanced authentication API v2
"""

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas.auth import CurrentUser, TokenResponse, UserResponse
from app.utils import hash_password, verify_password
from app.utils.auth import create_access_token, get_current_user
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger("auth_v2")


@router.post("/register", response_model=TokenResponse)
async def register_v2(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(None),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Enhanced user registration with better logging and validation.
    """
    logger.info("User registration attempt", extra={"email": email})

    from app.utils.validators import validate_password

    validate_password(password)

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        logger.warning(
            "Registration failed - email already exists", extra={"email": email}
        )
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=email, name=name, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    logger.info(
        "User registered successfully", extra={"user_id": user.id, "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(id=user.id, email=user.email, name=user.name),
    )


@router.post("/login", response_model=TokenResponse)
async def login_v2(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Enhanced user login with better logging.
    """
    logger.info("User login attempt", extra={"email": username})

    result = await db.execute(select(User).where(User.email == username))
    user = result.scalar_one_or_none()

    if (
        not user
        or not user.hashed_password
        or not verify_password(password, user.hashed_password)
    ):
        logger.warning("Login failed - invalid credentials", extra={"email": username})
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    logger.info(
        "User logged in successfully", extra={"user_id": user.id, "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(id=user.id, email=user.email, name=user.name),
    )


@router.get("/me", response_model=UserResponse)
async def get_me_v2(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Enhanced user profile endpoint with logging.
    """
    logger.info("User profile request", extra={"user_id": current_user.id})

    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("User not found", extra={"user_id": current_user.id})
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.model_validate(user)
