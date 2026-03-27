"""Async SQLAlchemy engine/session setup."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from smart_resume.config import settings

engine = create_async_engine(settings.database_url, echo=settings.db_echo)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Provide an async DB session for FastAPI dependencies."""
    async with SessionLocal() as session:
        yield session
