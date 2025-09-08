# app/tests/test_tasks.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app import models
from app.main import app
from app.models import Task
from app.utils.auth import create_access_token


@pytest_asyncio.fixture
async def client(override_get_db):
    "Asynchronous client with overridden dependencies"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def authenticated_client(client, override_get_db, test_user):
    "Client authenticated with JWT token"
    token = create_access_token(data={"sub": str(test_user.id), "username": test_user.email})
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client


@pytest.mark.asyncio
async def test_create_task(authenticated_client, db_session, test_user):
    response = await authenticated_client.post(
        "/api/v1/tasks/",
        json={"title": "Test task", "description": "A test description"}
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "A test description"
    assert data["completed"] is False
    assert "id" in data
    assert data["id"] == test_user.id

    # Check in DB
    task = await db_session.get(models.Task, data["id"])
    assert task is not None
    assert task.title == "Test task"
    assert task.id == test_user.id


@pytest.mark.asyncio
async def test_read_tasks_pagination(authenticated_client, db_session, test_user):
    # Create 15 tasks
    for i in range(15):
        task = models.Task(title=f"Task {i}", user_id=test_user.id)
        db_session.add(task)
    await db_session.commit()

    # Get first 10
    response = await authenticated_client.get("/api/v1/tasks/?limit=10")
    data = response.json()
    assert len(data["tasks"]) == 10  # ✅ Now checks the tasks list
    assert data["total"] == 15
    assert data["skip"] == 0
    assert data["limit"] == 10


@pytest.mark.asyncio
async def test_read_task(authenticated_client, db_session, test_user):
    # Create task
    task = Task(title="Single task", user_id=test_user.id)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await authenticated_client.get(f"/api/v1/tasks/{task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == "Single task"
    assert data["user_id"] == test_user.id


@pytest.mark.asyncio
async def test_read_task_not_found(authenticated_client):
    response = await authenticated_client.get("/api/v1/tasks/99999")
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_task(authenticated_client, db_session, test_user):
    # Create task
    task = Task(title="Old title", user_id=test_user.id)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await authenticated_client.put(
        f"/api/v1/tasks/{task.id}",
        json={"title": "Updated title", "completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["completed"] is True

    # Verify in DB
    updated_task = await db_session.get(Task, task.id)
    assert updated_task is not None
    assert updated_task.title == "Updated title"
    assert updated_task.completed is True


@pytest.mark.asyncio
async def test_update_task_not_found(authenticated_client):
    response = await authenticated_client.put(
        "/api/v1/tasks/99999",
        json={"title": "No existe"}
    )
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_task(authenticated_client, db_session, test_user):
    # Create task
    task = Task(title="To delete", user_id=test_user.id)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await authenticated_client.delete(f"/api/v1/tasks/{task.id}")
    assert response.status_code == 200
    assert "Task deleted" in response.json()["detail"]

    # Verify it was deleted
    deleted_task = await db_session.get(Task, task.id)
    assert deleted_task is None


@pytest.mark.asyncio
async def test_delete_task_not_found(authenticated_client):
    response = await authenticated_client.delete("/api/v1/tasks/99999")
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_task_unauthenticated(client):
    response = await client.post("/api/v1/tasks/", json={"title": "No auth"})
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_read_tasks_unauthenticated(client):
    response = await client.get("/api/v1/tasks/")
    assert response.status_code == 401
    assert "detail" in response.json()
