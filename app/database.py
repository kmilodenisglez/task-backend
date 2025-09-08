# app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def get_database_url():
    if settings.testing:
        # Use file-based SQLite for testing
        return "sqlite+aiosqlite:///test.db"
        # return "sqlite+aiosqlite:///:memory:"
    return settings.database_url.replace("postgresql+psycopg2", "postgresql+asyncpg")


DATABASE_URL = get_database_url()

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)


async def get_db():
    async with async_session_maker() as session:
        yield session
