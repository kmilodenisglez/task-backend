# app/schemas/auth.py
from pydantic import BaseModel
from typing import Optional

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

    class Config:
        from_attributes = True

class UserSession(BaseModel):
    id: int
    email: str
    name: Optional[str] = None


class AuthStatus(BaseModel):
    authenticated: bool
    user: Optional[UserSession] = None