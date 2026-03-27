"""Unit tests for authentication API routes."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from smart_resume.api.app import app
from smart_resume.db.base import Base
from smart_resume.db.engine import get_db


@pytest.fixture
async def auth_client() -> AsyncIterator[AsyncClient]:
    """Provide an API client backed by an in-memory async SQLite DB."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_register_creates_user(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/auth/register",
        json={"email": "User@Test.com", "password": "secret123", "full_name": "Test User"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"]
    assert payload["email"] == "user@test.com"


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_conflict(auth_client: AsyncClient) -> None:
    payload = {"email": "dup@test.com", "password": "secret123", "full_name": "Dup User"}
    first = await auth_client.post("/api/v1/auth/register", json=payload)
    second = await auth_client.post("/api/v1/auth/register", json=payload)

    assert first.status_code == 200
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_returns_bearer_token(auth_client: AsyncClient) -> None:
    register_payload = {"email": "login@test.com", "password": "secret123", "full_name": "Login User"}
    register = await auth_client.post("/api/v1/auth/register", json=register_payload)
    assert register.status_code == 200

    login = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "secret123"},
    )
    assert login.status_code == 200
    token_payload = login.json()
    assert token_payload["token_type"] == "bearer"
    assert isinstance(token_payload["access_token"], str)
    assert token_payload["access_token"]
