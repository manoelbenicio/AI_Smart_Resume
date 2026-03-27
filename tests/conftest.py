"""Shared test fixtures and configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_cv_text() -> str:
    """Load sample CV text fixture."""
    return (FIXTURES_DIR / "sample_cv.txt").read_text(encoding="utf-8")


@pytest.fixture
def sample_jd_text() -> str:
    """Load sample Job Description text fixture."""
    return (FIXTURES_DIR / "sample_jd.txt").read_text(encoding="utf-8")
