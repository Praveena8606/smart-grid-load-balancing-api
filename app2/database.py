from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

SYNC_DATABASE_URL = "postgresql://postgres:12345@localhost:5434/tsdb"

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# ---------- Async Database (FastAPI) ----------
ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:12345@localhost:5434/tsdb"

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session