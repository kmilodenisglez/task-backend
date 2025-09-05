# app/tests/test_tasks.py
from app.models import Task

def test_create_task(client, db_session):
    response = client.post("/api/v1/tasks/", json={"title": "Test task"})
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["title"] == "Test task"
    assert data["completed"] is False
    assert "id" in data

    # Check in DB (synchronous)
    task = db_session.query(Task).filter(Task.id == data["id"]).first()
    assert task is not None
    assert task.title == "Test task"

def test_read_tasks(client, db_session):
    # Create tasks directly in the database (synchronous)
    task1 = Task(title="Task 1")
    task2 = Task(title="Task 2")
    db_session.add_all([task1, task2])
    db_session.commit()  # Synchronous, without await
    db_session.refresh(task1)
    db_session.refresh(task2)

    # Read all
    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200
    data = response.json()
    titles = [task["title"] for task in data]
    assert "Task 1" in titles
    assert "Task 2" in titles