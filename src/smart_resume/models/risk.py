"""Risk Assessment and Distinctiveness output models."""

from __future__ import annotations

from pydantic import Field

from smart_resume.models.base import LLMSafeModel


class RiskItem(LLMSafeModel):
    """A single risk category assessment."""

    level: str = "Unknown"  # Low | Medium | High | Critical
    explanation: str = ""


class RiskAssessment(LLMSafeModel):
    """Full output of the Risk Assessment Agent."""

    risks: dict[str, RiskItem] = Field(default_factory=dict)


class DistinctivenessResult(LLMSafeModel):
    """Output of the Distinctiveness Agent."""

    differentiators: list[str] = Field(default_factory=list)
    is_commodity: bool = True
    commodity_rationale: str = ""
    weaknesses: list[str] = Field(default_factory=list)
