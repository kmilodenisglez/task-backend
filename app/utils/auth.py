# app/utils/auth.py
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request, status

# Custom OAuth2 for Swagger (Password Flow)
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.schemas.auth import CurrentUser

# Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hashing functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


class OAuth2PasswordBearerWithBearer(OAuth2):
    def __init__(self, tokenUrl: str):
        flows = OAuthFlowsModel(password=OAuthFlowPassword(tokenUrl=tokenUrl))
        super().__init__(
            flows=flows, scheme_name="Bearer", auto_error=True
        )  # 👈 forzar 401


class OAuth2PasswordBearer401(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str:
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await super().__call__(request)


oauth2_scheme = OAuth2PasswordBearer401(tokenUrl="/api/v1/auth/login")


# Dependency for current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not str(user_id).isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return CurrentUser(id=int(user_id), email=email)
