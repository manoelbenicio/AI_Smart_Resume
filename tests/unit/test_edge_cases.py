"""Edge-case tests for LLMSafeModel coercion paths and model defaults."""

from __future__ import annotations

from smart_resume.models.cv import CVData, Education, Experience
from smart_resume.models.job import JobDescription
from smart_resume.models.risk import RiskAssessment
from smart_resume.models.scores import ScoringResult


class TestEdgeCases:
    """Validate model behavior against LLM-style inconsistent payloads."""

    def test_cvdata_empty_payload_defaults(self) -> None:
        cv = CVData.model_validate({})
        assert cv.personal.name == ""
        assert cv.experience == []
        assert cv.education == []
        assert cv.skills == []

    def test_cvdata_minimal_personal_empty_name(self) -> None:
        cv = CVData.model_validate({"personal": {"name": ""}})
        assert cv.personal.name == ""
        assert cv.personal.email is None
        assert cv.personal.phone is None

    def test_experience_period_none_coerces_to_default_period(self) -> None:
        exp = Experience.model_validate({"company": "Acme", "role": "CTO", "period": None})
        assert exp.period.start == ""
        assert exp.period.end is None

    def test_experience_period_string_coerces_to_start_end(self) -> None:
        exp = Experience.model_validate({"company": "Acme", "role": "CTO", "period": "2020-2024"})
        assert exp.period.start == "2020"
        assert exp.period.end == "2024"

    def test_experience_period_dict_with_start_only(self) -> None:
        exp = Experience.model_validate(
            {"company": "Acme", "role": "CTO", "period": {"start": "2020"}}
        )
        assert exp.period.start == "2020"
        assert exp.period.end is None

    def test_education_year_int_coerces_to_string(self) -> None:
        edu = Education.model_validate({"degree": "MBA", "institution": "MIT", "year": 2012})
        assert edu.year == "2012"

    def test_education_year_none_preserved(self) -> None:
        edu = Education.model_validate({"degree": "MBA", "institution": "MIT", "year": None})
        assert edu.year is None

    def test_education_year_string_preserved(self) -> None:
        edu = Education.model_validate({"degree": "MBA", "institution": "MIT", "year": "2012"})
        assert edu.year == "2012"

    def test_job_description_none_lists_coerce_to_empty_lists(self) -> None:
        jd = JobDescription.model_validate(
            {
                "responsibilities": None,
                "required_skills": None,
                "desired_qualifications": None,
                "quantifiable_requirements": None,
            }
        )
        assert jd.responsibilities == []
        assert jd.required_skills == []
        assert jd.desired_qualifications == []
        assert jd.quantifiable_requirements == []

    def test_scoring_result_missing_category_scores_uses_default_factory(self) -> None:
        result = ScoringResult.model_validate({"overall_score": 78.5, "explanations": {"scale": "ok"}})
        assert result.overall_score == 78.5
        assert result.category_scores.scale == 0
        assert result.category_scores.executive_presence == 0

    def test_scoring_result_accepts_human_friendly_score_keys(self) -> None:
        result = ScoringResult.model_validate(
            {
                "category_scores": {
                    "Scale of operations": 72,
                    "Strategic Complexity of initiatives": 85,
                    "Executive Presence & Branding": 80,
                },
                "overall_score": 80.0,
                "explanations": {
                    "Scale of operations": "Managed broad operations.",
                    "Executive Presence & Branding": "Board-level communication.",
                },
            }
        )
        assert result.category_scores.scale == 72
        assert result.category_scores.strategic_complexity == 85
        assert result.category_scores.executive_presence == 80
        assert result.explanations["scale"] == "Managed broad operations."
        assert result.explanations["executive_presence"] == "Board-level communication."

    def test_risk_assessment_with_empty_risks_dict(self) -> None:
        risk = RiskAssessment.model_validate({"risks": {}})
        assert risk.risks == {}
