"""Unit tests for file parsers."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestTextParsing:
    """Test text file ingestion."""

    def test_read_txt(self, sample_cv_text: str) -> None:
        assert "John A. Executive" in sample_cv_text
        assert "Chief Technology Officer" in sample_cv_text
        assert len(sample_cv_text) > 100

    def test_read_jd(self, sample_jd_text: str) -> None:
        assert "MegaCorp International" in sample_jd_text
        assert "CTO" in sample_jd_text or "Chief Technology Officer" in sample_jd_text
