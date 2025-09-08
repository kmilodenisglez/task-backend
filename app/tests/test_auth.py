# app/tests/test_auth.py

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.utils.auth import create_access_token

# @pytest.fixture(autouse=True)
# async def clean_db(db_session):
#     # Clear the 'users' table before each test
#     await db_session.execute(text("DELETE FROM users"))
#     await db_session.commit()


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Task API"}


@pytest.mark.asyncio
async def test_login_success(db_session, test_user):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "T3stp@ssw0rd.23"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == test_user.email
    assert data["user"]["id"] == test_user.id


@pytest.mark.asyncio
async def test_login_invalid_credentials(db_session, test_user):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": test_user.email, "password": "Wr0ng-p@ssWd"},
        )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_me_with_valid_jwt(override_get_db, test_user):
    token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name


@pytest.mark.asyncio
async def test_me_with_not_found_user(override_get_db):
    token = create_access_token(data={"sub": "99999", "email": "email@no.me"})

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_me_with_invalid_token():
    token = create_access_token(data={})

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/auth/me",
        )
    assert response.status_code == 401
    assert "detail" in response.json()
