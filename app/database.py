from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import DATABASE_URL
import os

load_dotenv()

import re

# Replace driver for async
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    # asyncpg expects 'ssl' instead of 'sslmode'
    ASYNC_DATABASE_URL = re.sub(r"([?&])sslmode=", r"\1ssl=", ASYNC_DATABASE_URL)
    # asyncpg doesn't support 'channel_binding' (remove it completely)
    ASYNC_DATABASE_URL = re.sub(r"([?&])channel_binding=[^&]*", "", ASYNC_DATABASE_URL)
    # cleanup dangling ampersands if channel_binding was first
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("?&", "?")
    if ASYNC_DATABASE_URL.endswith("?"):
        ASYNC_DATABASE_URL = ASYNC_DATABASE_URL[:-1]
elif DATABASE_URL.startswith("sqlite:///"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create async engine
engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as db:
        yield db