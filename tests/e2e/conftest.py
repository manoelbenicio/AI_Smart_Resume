"""E2E test configuration."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from smart_resume.config import settings


@pytest.fixture(autouse=True)
def enable_auth_for_e2e() -> Iterator[None]:
    """Force auth-on behavior for E2E API contract validation."""
    original = settings.auth_enabled
    settings.auth_enabled = True
    try:
        yield
    finally:
        settings.auth_enabled = original
