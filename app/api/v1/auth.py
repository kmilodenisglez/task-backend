from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils import hash_password, verify_password
from app.utils.validators import validate_password

# load environment variables from .env
load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("/register")
async def register(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        name: str = Form(None),
        db: Session = Depends(get_db),
):
    # Password validation
    validate_password(password)

    # Check if user already exists using modern SQLAlchemy syntax
    existing_user = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=email, name=name, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    # Optionally log in the user after registration
    request.session["user"] = {"id": user.id, "email": user.email, "name": user.name}
    return {
        "message": "User registered",
        "user": {"id": user.id, "email": user.email, "name": user.name},
    }


@router.post("/login")
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db),
):
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if (
            not user
            or user.hashed_password is None
            or not verify_password(password, user.hashed_password)
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["user"] = {"id": user.id, "email": user.email, "name": user.name}
    return {
        "message": "Logged in",
        "user": {"id": user.id, "email": user.email, "name": user.name},
    }


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


@router.get("/me")
async def get_me(request: Request):
    user = request.session.get("user")
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, "user": user}


@router.post("/test-login")
async def test_login(request: Request):
    # Simulate a user login for testing
    request.session["user"] = {"id": 1, "email": "test@example.com", "name": "Test"}
    return {"message": "logged in"}
