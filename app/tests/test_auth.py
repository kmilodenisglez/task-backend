# app/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.config import settings
from app.main import app
from app.models import User
from app.database import get_db, async_session
from app.utils.auth import hash_password

client = TestClient(app)


def create_jwt_token(user_id: int) -> str:
    """Helper: crea un token JWT para un usuario"""
    from datetime import datetime, timedelta
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


@pytest.fixture
async def test_user():
    """Crea un usuario de prueba en la DB"""
    async with async_session() as session:
        user = User(
            email="testuser@example.com",
            name="Test User",
            hashed_password=hash_password("testpassword123")
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        yield user
        await session.delete(user)
        await session.commit()


def test_me_with_valid_jwt(test_user):
    # 1. Crear token
    token = create_jwt_token(test_user.id)

    # 2. Llamar a /me con el token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 3. Verificar respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name


def test_me_with_invalid_token():
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_me_without_token():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401