"""Application configuration via environment variables."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global settings loaded from .env or environment variables."""

    # ─── LLM ───
    openai_api_key: str = ""
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 4096

    # ─── Application ───
    log_level: str = "INFO"
    output_dir: Path = Path("outputs")
    max_reeval_iterations: int = 3
    target_score: int = 90

    # ─── Auth ───
    auth_enabled: bool = False
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # ─── Database ───
    database_url: str = "postgresql+asyncpg://smartuser:smartpass@localhost:5432/smart_resume"
    db_echo: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton — import from here everywhere
settings = Settings()
