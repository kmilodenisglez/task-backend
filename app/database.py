# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

# Detect if we are in test mode
from app.config import settings

TESTING = settings.testing

if TESTING:
    # Synchronous mode for testing
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    DBSession = Session
else:
    # Asynchronous mode for production/development
    DATABASE_URL = settings.database_url.replace("postgresql+psycopg2", "postgresql+asyncpg")
    engine = create_async_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    DBSession = AsyncSession

# get_db function that works for both modes
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        if TESTING:
            db.close()  # Síncrono
        else:
            await db.close()  # Asíncrono