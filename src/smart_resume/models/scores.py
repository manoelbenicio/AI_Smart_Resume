"""Scoring and Benchmark output models."""

from __future__ import annotations

import re
from typing import Any

from pydantic import Field, model_validator

from smart_resume.models.base import LLMSafeModel


def _normalize_score_key(raw_key: str) -> str:
    """Normalize arbitrary score keys from LLM output to a comparable token."""
    return re.sub(r"[^a-z0-9]+", " ", raw_key.lower()).strip()


def _canonical_score_key(raw_key: str) -> str | None:
    """Map common LLM-provided score key variants to model field names."""
    key = _normalize_score_key(raw_key)

    key_map = {
        "scale": "scale",
        "scale of operations": "scale",
        "strategic complexity": "strategic_complexity",
        "strategic complexity of initiatives": "strategic_complexity",
        "transformation history": "transformation_history",
        "competitive differentiation": "competitive_differentiation",
        "international experience": "international_experience",
        "career progression speed": "career_progression_speed",
        "financial impact": "financial_impact",
        "executive presence": "executive_presence",
        "executive presence branding": "executive_presence",
    }

    if key in key_map:
        return key_map[key]

    if "scale" in key and "operation" in key:
        return "scale"
    if "strategic" in key and "complex" in key:
        return "strategic_complexity"
    if "transformation" in key:
        return "transformation_history"
    if "competitive" in key and "different" in key:
        return "competitive_differentiation"
    if "international" in key:
        return "international_experience"
    if "career" in key and "progress" in key:
        return "career_progression_speed"
    if "financial" in key and "impact" in key:
        return "financial_impact"
    if "executive" in key and "presence" in key:
        return "executive_presence"
    return None


class CategoryScores(LLMSafeModel):
    """Individual category scores from the Scoring Agent (0–100 each)."""

    scale: float = 0
    strategic_complexity: float = 0
    transformation_history: float = 0
    competitive_differentiation: float = 0
    international_experience: float = 0
    career_progression_speed: float = 0
    financial_impact: float = 0
    executive_presence: float = 0

    @model_validator(mode="before")
    @classmethod
    def _normalize_category_keys(cls, data: Any) -> Any:
        """Coerce common non-snake-case key variants into canonical field names."""
        if not isinstance(data, dict):
            return data

        normalized: dict[str, Any] = {}
        for key, value in data.items():
            canonical = _canonical_score_key(str(key))
            if canonical:
                normalized[canonical] = value
            else:
                normalized[str(key)] = value
        return normalized


class ScoringResult(LLMSafeModel):
    """Full output of the Scoring Agent."""

    category_scores: CategoryScores = Field(default_factory=CategoryScores)
    overall_score: float = 0
    explanations: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _normalize_explanation_keys(cls, data: Any) -> Any:
        """Normalize explanation keys so CLI can match them to score fields."""
        if not isinstance(data, dict):
            return data

        explanations = data.get("explanations")
        if isinstance(explanations, dict):
            normalized_explanations: dict[str, str] = {}
            for key, value in explanations.items():
                canonical = _canonical_score_key(str(key))
                target_key = canonical or str(key)
                normalized_explanations[target_key] = str(value)
            data["explanations"] = normalized_explanations

        return data


class BenchmarkResult(LLMSafeModel):
    """Output of the Benchmark Agent — archetype comparisons."""

    benchmark: dict[str, str] = Field(default_factory=dict)
    rationales: dict[str, str] = Field(default_factory=dict)


class ReEvaluationResult(LLMSafeModel):
    """Output of the Re-Evaluation Agent."""

    score: float = 0
    explanation: str = ""
    recommendations: list[str] = Field(default_factory=list)
