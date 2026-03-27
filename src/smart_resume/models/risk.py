"""Risk Assessment and Distinctiveness output models."""

from __future__ import annotations

from pydantic import Field, field_validator

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

    @field_validator("is_commodity", mode="before")
    @classmethod
    def _coerce_is_commodity(cls, value: object) -> bool:
        """Handle non-boolean LLM outputs like 'irreplaceable'/'commodity'."""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "yes", "y", "1", "commodity", "replaceable", "generic"}:
                return True
            if normalized in {"false", "no", "n", "0", "irreplaceable", "unique", "non-commodity"}:
                return False
            if "not" in normalized and "commodity" in normalized:
                return False
            if "irreplace" in normalized or "unique" in normalized:
                return False
            if "replace" in normalized or "commodity" in normalized:
                return True
        return True
