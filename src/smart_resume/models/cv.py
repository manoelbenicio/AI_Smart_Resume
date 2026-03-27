"""CV data models — structured representation of a candidate's curriculum vitae.

All models inherit from ``LLMSafeModel`` for universal LLM output tolerance.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from smart_resume.models.base import LLMSafeModel


class PersonalInfo(LLMSafeModel):
    """Candidate's personal / contact information."""

    name: str = ""
    email: str | None = None
    phone: str | None = None


class ExperiencePeriod(LLMSafeModel):
    """Start/end date range for a role."""

    start: str = ""
    end: str | None = None


class Experience(LLMSafeModel):
    """A single employment record."""

    company: str = ""
    role: str = ""
    location: str | None = None
    period: ExperiencePeriod = Field(default_factory=ExperiencePeriod)
    achievements: list[str] = Field(default_factory=list)

    @field_validator("period", mode="before")
    @classmethod
    def _coerce_period(cls, v: Any) -> Any:
        """LLMs may return period as a plain string like '2020-2024'."""
        if isinstance(v, str):
            parts = v.split("-", 1) if "-" in v else v.split("–", 1)
            return {"start": parts[0].strip(), "end": parts[1].strip() if len(parts) > 1 else None}
        if v is None:
            return {}
        return v


class Education(LLMSafeModel):
    """An educational qualification."""

    degree: str = ""
    institution: str = ""
    year: str | None = None

    @field_validator("year", mode="before")
    @classmethod
    def _coerce_year(cls, v: Any) -> str | None:
        """LLMs may return year as int (2012) instead of str ('2012')."""
        if isinstance(v, int):
            return str(v)
        return v


class CVData(LLMSafeModel):
    """Full structured CV extracted by the Extraction Agent."""

    personal: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: str | None = None
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    awards: list[str] = Field(default_factory=list)
