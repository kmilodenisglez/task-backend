# app/schemas/auth.py
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LoginForm(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    email: str
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    email: str
    name: str | None

    model_config = ConfigDict(from_attributes=True)


class UserSession(BaseModel):
    id: int
    email: str
    name: Optional[str] = None


class CurrentUser(BaseModel):
    id: int
    email: Optional[str] = None


class AuthStatus(BaseModel):
    authenticated: bool
    user: Optional[UserSession] = None


class TokenResponse(Token):
    token_type: str = "bearer"
    user: UserResponse
