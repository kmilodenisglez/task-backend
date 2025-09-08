# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

# Usa asyncpg en todos los entornos
DATABASE_URL = settings.database_url.replace("postgresql+psycopg2", "postgresql+asyncpg")

if settings.testing:
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession, autoflush=False,
                                   autocommit=False, )


async def get_db():
    async with async_session_maker() as session:
        yield session
