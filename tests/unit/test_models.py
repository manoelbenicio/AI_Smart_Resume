"""Unit tests for Pydantic data models."""

from __future__ import annotations

import pytest

from smart_resume.models.cv import CVData, Education, Experience, ExperiencePeriod, PersonalInfo
from smart_resume.models.job import JobDescription
from smart_resume.models.risk import DistinctivenessResult, RiskAssessment, RiskItem
from smart_resume.models.scores import BenchmarkResult, CategoryScores, ReEvaluationResult, ScoringResult


class TestCVModels:
    """Test CV data model validation and serialization."""

    def test_personal_info_minimal(self) -> None:
        info = PersonalInfo(name="John Doe")
        assert info.name == "John Doe"
        assert info.email is None
        assert info.phone is None

    def test_personal_info_full(self) -> None:
        info = PersonalInfo(name="Jane Doe", email="jane@test.com", phone="+1-555-0000")
        assert info.email == "jane@test.com"

    def test_experience_model(self) -> None:
        exp = Experience(
            company="Acme Corp",
            role="CTO",
            location="NYC",
            period=ExperiencePeriod(start="2020", end="2024"),
            achievements=["Led transformation", "Saved $10M"],
        )
        assert len(exp.achievements) == 2
        assert exp.period.start == "2020"

    def test_cv_data_full_roundtrip(self) -> None:
        cv = CVData(
            personal=PersonalInfo(name="Test"),
            summary="A summary",
            experience=[
                Experience(
                    company="Co",
                    role="Role",
                    period=ExperiencePeriod(start="2020"),
                    achievements=["Did stuff"],
                )
            ],
            education=[Education(degree="MBA", institution="MIT")],
            certifications=["AWS"],
            skills=["Python"],
            languages=["English"],
            awards=["Best Employee"],
        )
        data = cv.model_dump()
        cv2 = CVData.model_validate(data)
        assert cv2.personal.name == "Test"
        assert len(cv2.experience) == 1

    def test_cv_data_minimal(self) -> None:
        cv = CVData(personal=PersonalInfo(name="Min"))
        assert cv.experience == []
        assert cv.skills == []


class TestJobModels:
    """Test Job Description model."""

    def test_job_description_full(self) -> None:
        jd = JobDescription(
            company="MegaCorp",
            title="CTO",
            location="NYC",
            responsibilities=["Lead tech"],
            required_skills=["Cloud"],
            desired_qualifications=["MBA"],
            quantifiable_requirements=["$200M budget"],
        )
        assert jd.company == "MegaCorp"
        assert len(jd.responsibilities) == 1

    def test_job_description_empty(self) -> None:
        jd = JobDescription()
        assert jd.company is None
        assert jd.responsibilities == []


class TestScoringModels:
    """Test scoring and benchmark models."""

    def test_category_scores_defaults(self) -> None:
        scores = CategoryScores()
        assert scores.scale == 0
        assert scores.executive_presence == 0

    def test_scoring_result(self) -> None:
        result = ScoringResult(
            category_scores=CategoryScores(scale=80, strategic_complexity=75),
            overall_score=77.5,
            explanations={"scale": "Strong budget management"},
        )
        assert result.overall_score == 77.5

    def test_benchmark_result(self) -> None:
        result = BenchmarkResult(
            benchmark={"fortune100": "Above Average", "bigTech": "Average"},
            rationales={"fortune100": "Good scale"},
        )
        assert result.benchmark["fortune100"] == "Above Average"

    def test_reeval_result(self) -> None:
        result = ReEvaluationResult(score=92, explanation="Good match", recommendations=[])
        assert result.score >= 90


class TestRiskModels:
    """Test risk and distinctiveness models."""

    def test_risk_item(self) -> None:
        item = RiskItem(level="High", explanation="Missing global exposure")
        assert item.level == "High"

    def test_risk_assessment(self) -> None:
        ra = RiskAssessment(
            risks={
                "scale": RiskItem(level="Low", explanation="Good scale"),
                "international_exposure": RiskItem(level="High", explanation="Limited"),
            }
        )
        assert len(ra.risks) == 2

    def test_distinctiveness(self) -> None:
        result = DistinctivenessResult(
            differentiators=["AI leadership", "M&A experience", "Global reach"],
            is_commodity=False,
            commodity_rationale="Unique combination of skills",
            weaknesses=["No board experience"],
        )
        assert not result.is_commodity
        assert len(result.differentiators) == 3

    def test_distinctiveness_coerces_string_commodity_flags(self) -> None:
        result = DistinctivenessResult.model_validate(
            {
                "differentiators": ["Global transformation experience"],
                "is_commodity": "irreplaceable",
                "commodity_rationale": "Rare mix of scale and strategy",
                "weaknesses": [],
            }
        )
        assert result.is_commodity is False
