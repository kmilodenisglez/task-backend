# conftest.py
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings

settings.testing = True

# Now import after settings are applied
from app.database import DATABASE_URL, get_db
from app.main import app
from app.models import Base

# Engine de test
test_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest_asyncio.fixture(scope="session", autouse=True) # autouse=True ensures tables are created once before any test. 
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    print("================  db_session  ================ ")
    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def override_get_db(db_session):
    print("================  override_get_db  ================ ")
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()