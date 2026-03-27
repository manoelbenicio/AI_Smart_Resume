"""Unit tests for LLMSafeModel.safe_parse and coercion guards."""

from __future__ import annotations

import logging

import pytest

from smart_resume.models.cv import CVData
from smart_resume.models.job import JobDescription
from smart_resume.models.scores import ScoringResult


def test_safe_parse_returns_defaults_on_validation_error(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        result = ScoringResult.safe_parse({"category_scores": "not-an-object", "overall_score": "NaN"})

    assert result.overall_score == 0
    assert result.category_scores.scale == 0
    assert "LLM model validation failed for ScoringResult" in caplog.text


def test_scores_coerce_numeric_strings() -> None:
    result = ScoringResult.safe_parse(
        {
            "category_scores": {"scale": "91", "strategic_complexity": "87.5"},
            "overall_score": "89.25",
            "explanations": {},
        }
    )
    assert result.category_scores.scale == 91
    assert result.category_scores.strategic_complexity == 87.5
    assert result.overall_score == 89.25


def test_cv_coerces_string_fields_to_lists() -> None:
    result = CVData.safe_parse({"personal": {"name": "Alice"}, "skills": "Python", "certifications": "AWS"})
    assert result.skills == ["Python"]
    assert result.certifications == ["AWS"]


def test_job_coerces_string_fields_to_lists() -> None:
    result = JobDescription.safe_parse(
        {"responsibilities": "Lead platform engineering", "required_skills": "Cloud Architecture"}
    )
    assert result.responsibilities == ["Lead platform engineering"]
    assert result.required_skills == ["Cloud Architecture"]
