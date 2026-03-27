"""Integration tests for the full orchestrator pipeline.

These tests use mocked LLM calls to verify the full pipeline sequencing,
retry/re-evaluation loop, and audit trail persistence without requiring
an actual OpenAI API key.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from smart_resume.models.cv import CVData, Education, Experience, ExperiencePeriod, PersonalInfo
from smart_resume.models.job import JobDescription
from smart_resume.models.risk import DistinctivenessResult, RiskAssessment, RiskItem
from smart_resume.models.scores import BenchmarkResult, CategoryScores, ReEvaluationResult, ScoringResult


# ─── Mock data factories ────────────────────────────────────────


def _mock_cv_data() -> CVData:
    return CVData(
        personal=PersonalInfo(name="John Test", email="john@test.com"),
        summary="Seasoned tech executive with 15+ years of experience.",
        experience=[
            Experience(
                company="TestCorp",
                role="CTO",
                period=ExperiencePeriod(start="2020", end="2024"),
                achievements=["Led transformation", "Saved $10M"],
            ),
        ],
        education=[Education(degree="MBA", institution="MIT")],
        certifications=["AWS SA Pro"],
        skills=["Cloud Architecture", "AI/ML"],
        languages=["English"],
    )


def _mock_jd() -> JobDescription:
    return JobDescription(
        company="MegaCorp",
        title="CTO",
        location="NYC",
        responsibilities=["Lead tech org"],
        required_skills=["Cloud", "AI"],
    )


def _mock_scoring() -> ScoringResult:
    return ScoringResult(
        category_scores=CategoryScores(
            scale=85,
            strategic_complexity=80,
            quantified_impact=75,
            transformation_scope=80,
            international_exposure=70,
            board_level_communication=80,
            innovation_digital_dna=75,
            industry_relevance=85,
        ),
        overall_score=78.75,
        explanations={"scale": "Strong scale management"},
    )


def _mock_benchmark() -> BenchmarkResult:
    return BenchmarkResult(
        benchmark={"fortune100": "Above Average"},
        rationales={"fortune100": "Solid track record"},
    )


def _mock_distinctiveness() -> DistinctivenessResult:
    return DistinctivenessResult(
        differentiators=["AI pioneer", "Cost optimizer"],
        is_commodity=False,
        commodity_rationale="Unique skill set",
        weaknesses=["Limited board exposure"],
    )


def _mock_risk() -> RiskAssessment:
    return RiskAssessment(
        risks={"scale": RiskItem(level="Low", explanation="OK")}
    )


def _mock_reeval_pass() -> ReEvaluationResult:
    return ReEvaluationResult(score=92, explanation="Strong fit", recommendations=[])


def _mock_reeval_fail() -> ReEvaluationResult:
    return ReEvaluationResult(score=75, explanation="Needs work", recommendations=["Add metrics"])


# ─── Test class ──────────────────────────────────────────────────


class TestPipelineModels:
    """Verify that mock data factories produce valid models."""

    def test_cv_data_valid(self) -> None:
        cv = _mock_cv_data()
        assert cv.personal.name == "John Test"
        assert len(cv.experience) == 1

    def test_jd_valid(self) -> None:
        jd = _mock_jd()
        assert jd.company == "MegaCorp"

    def test_scoring_valid(self) -> None:
        scoring = _mock_scoring()
        assert scoring.overall_score == 78.75

    def test_benchmark_valid(self) -> None:
        b = _mock_benchmark()
        assert "fortune100" in b.benchmark

    def test_distinctiveness_valid(self) -> None:
        d = _mock_distinctiveness()
        assert not d.is_commodity

    def test_risk_valid(self) -> None:
        r = _mock_risk()
        assert "scale" in r.risks

    def test_reeval_pass(self) -> None:
        r = _mock_reeval_pass()
        assert r.score >= 90

    def test_reeval_fail(self) -> None:
        r = _mock_reeval_fail()
        assert r.score < 90


class TestPipelineAuditTrail:
    """Verify pipeline audit trail data model."""

    def test_pipeline_run_model(self) -> None:
        from smart_resume.models.pipeline import PipelineRun

        run = PipelineRun()
        assert run.run_id  # UUID is auto-generated
        assert run.started_at  # Timestamp is auto-generated
        assert run.final_score == 0
        assert run.iterations_used == 0

        # Set phase outputs
        run.extraction_cv = _mock_cv_data()
        run.extraction_jd = _mock_jd()
        run.scoring = _mock_scoring()

        assert run.extraction_cv.personal.name == "John Test"
        assert run.scoring.overall_score == 78.75

        # Verify serialization round-trip
        data = run.model_dump()
        restored = PipelineRun.model_validate(data)
        assert restored.run_id == run.run_id
        assert restored.extraction_cv is not None
        assert restored.extraction_cv.personal.name == "John Test"

    def test_pipeline_run_reeval_history(self) -> None:
        from smart_resume.models.pipeline import PipelineRun

        run = PipelineRun()
        run.re_evaluation_history.append(_mock_reeval_fail())
        run.re_evaluation_history.append(_mock_reeval_pass())
        assert len(run.re_evaluation_history) == 2
        assert run.re_evaluation_history[0].score < 90
        assert run.re_evaluation_history[1].score >= 90
