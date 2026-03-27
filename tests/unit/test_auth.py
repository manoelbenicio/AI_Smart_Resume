"""Unit tests for JWT auth helpers and current-user dependency."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from smart_resume.api.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from smart_resume.config import settings


@pytest.fixture
def auth_settings_guard() -> None:
    """Preserve auth-related settings across tests."""
    original_enabled = settings.auth_enabled
    original_secret = settings.jwt_secret_key
    original_algo = settings.jwt_algorithm
    original_exp = settings.jwt_expire_minutes
    try:
        yield
    finally:
        settings.auth_enabled = original_enabled
        settings.jwt_secret_key = original_secret
        settings.jwt_algorithm = original_algo
        settings.jwt_expire_minutes = original_exp


def test_password_hash_and_verify_round_trip(auth_settings_guard: None) -> None:
    password = "super-secret-password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


@pytest.mark.asyncio
async def test_get_current_user_valid_token(auth_settings_guard: None) -> None:
    settings.auth_enabled = True
    token = create_access_token({"sub": "user-123", "email": "user@test.com"}, expires_minutes=5)
    user = await get_current_user(token)
    assert user.user_id == "user-123"
    assert user.email == "user@test.com"


@pytest.mark.asyncio
async def test_get_current_user_expired_token(auth_settings_guard: None) -> None:
    settings.auth_enabled = True
    token = create_access_token({"sub": "user-123", "email": "user@test.com"}, expires_minutes=-1)
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_missing_token(auth_settings_guard: None) -> None:
    settings.auth_enabled = True
    with pytest.raises(HTTPException) as exc:
        await get_current_user(None)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_auth_disabled_returns_anonymous(auth_settings_guard: None) -> None:
    settings.auth_enabled = False
    user = await get_current_user(None)
    assert user.user_id == "anonymous"
    assert user.email == "local@dev"
