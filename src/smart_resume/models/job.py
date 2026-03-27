"""Job Description data models."""

from __future__ import annotations

from pydantic import Field

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
