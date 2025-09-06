# app/api/v1/auth.py
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, DBSession
from app.models import User
from app.schemas import Token, UserResponse
from app.utils import hash_password, verify_password
from app.utils.auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(Token):
    token_type: str = "bearer"


@router.post("/register", response_model=TokenResponse)
async def register(
        email: str = Form(...),
        password: str = Form(...),
        name: str = Form(None),
        db: DBSession = Depends(get_db),
):
    from app.utils.validators import validate_password
    validate_password(password)

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=email, name=name, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "name": user.name},
    }


@router.post("/login", response_model=TokenResponse)
async def login(
        email: str = Form(...),
        password: str = Form(...),
        db: DBSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "name": user.name},
    }

@router.get("/me", response_model=UserResponse)
async def get_me(
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == current_user["id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user