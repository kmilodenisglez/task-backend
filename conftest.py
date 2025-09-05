# conftest.py
import pytest
from app.main import app
from app.database import get_db
from app.tests.test_tasks import db_session


@pytest.fixture(autouse=True)
def override_get_db():
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()