import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# ----------------------------------------
# Database URLs
# ----------------------------------------

SYNC_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:12345@localhost:5434/tsdb"
)

ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL",
    "postgresql+asyncpg://postgres:12345@localhost:5434/tsdb"
)

# ----------------------------------------
# Sync Engine (Celery)
# ----------------------------------------

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

# ----------------------------------------
# Async Engine (FastAPI)
# ----------------------------------------

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ----------------------------------------
# Base
# ----------------------------------------

Base = declarative_base()

# ----------------------------------------
# Dependency
# ----------------------------------------

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session