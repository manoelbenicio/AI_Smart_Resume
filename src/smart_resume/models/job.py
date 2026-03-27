"""Job Description data models."""

from __future__ import annotations

from typing import Any

from pydantic import Field
from pydantic import field_validator

from smart_resume.models.base import LLMSafeModel


class JobDescription(LLMSafeModel):
    """Structured job description extracted by the Extraction Agent."""

    company: str | None = None
    title: str | None = None
    location: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    desired_qualifications: list[str] = Field(default_factory=list)
    quantifiable_requirements: list[str] = Field(default_factory=list)

    @field_validator(
        "responsibilities",
        "required_skills",
        "desired_qualifications",
        "quantifiable_requirements",
        mode="before",
    )
    @classmethod
    def _coerce_to_list(cls, value: Any) -> list[str]:
        """Normalize noisy LLM outputs to list[str]."""
        if value is None:
            return []
        if isinstance(value, dict):
            return [f"{k}: {v}" for k, v in value.items()]
        if isinstance(value, str):
            return [value] if value.strip() else []
        if isinstance(value, list):
            normalized: list[str] = []
            for item in value:
                if isinstance(item, dict):
                    normalized.extend(f"{k}: {v}" for k, v in item.items())
                elif item is not None:
                    text = str(item).strip()
                    if text:
                        normalized.append(text)
            return normalized
        return [str(value)]
