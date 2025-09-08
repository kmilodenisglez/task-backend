# conftest.py
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import Base
from app.database import DATABASE_URL
from app.config import settings

settings.testing = True

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

@pytest_asyncio.fixture(scope="session")
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session