"""Unit tests for configuration module."""

from __future__ import annotations

import os

import pytest


class TestSettings:
    """Test Settings configuration class."""

    def test_settings_defaults(self) -> None:
        from smart_resume.config import Settings

        settings = Settings(openai_api_key="test-key-123")
        assert settings.llm_model == "gpt-4o"
        assert settings.target_score == 90
        assert settings.max_reeval_iterations == 3
        assert settings.log_level == "INFO"

    def test_settings_custom(self) -> None:
        from smart_resume.config import Settings

        settings = Settings(
            openai_api_key="test-key-456",
            llm_model="gpt-4-turbo",
            target_score=85,
            max_reeval_iterations=5,
            log_level="DEBUG",
        )
        assert settings.llm_model == "gpt-4-turbo"
        assert settings.target_score == 85
        assert settings.max_reeval_iterations == 5

    def test_settings_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "env-test-key")
        monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
        monkeypatch.setenv("TARGET_SCORE", "95")

        from smart_resume.config import Settings

        settings = Settings()  # type: ignore[call-arg]
        assert settings.openai_api_key == "env-test-key"
        assert settings.llm_model == "gpt-4o-mini"
        assert settings.target_score == 95
