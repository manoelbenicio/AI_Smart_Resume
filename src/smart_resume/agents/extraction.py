"""Phase 1 — Extraction Agent: CV + Job Description → structured JSON."""

from __future__ import annotations

from typing import Any

import structlog

from smart_resume.agents.base import BaseAgent
from smart_resume.models.cv import CVData
from smart_resume.models.job import JobDescription

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
You are a CV and Job Description Extraction Agent.  Given a candidate's CV and a job \
description, extract structured information into JSON format.

Steps:
1. Identify and extract from the CV: personal details (name, email, phone), summary \
statements, employment history (company, role, location, start–end dates, responsibilities, \
quantified achievements), education, certifications, skills, languages and awards.
2. For the job description, extract: company name, job title, location, major responsibilities, \
required skills, desired qualifications and any quantifiable requirements.
3. Return valid JSON with two top-level keys: "cv" and "job_description".  Use arrays for lists \
(e.g., "experience" with objects containing "company", "role", "period", "achievements").  \
If information is missing, set the corresponding field to null.
"""


class ExtractionAgent(BaseAgent):
    """Parse raw CV text and JD text into structured Pydantic models."""

    agent_name = "ExtractionAgent"

    def run(self, *, cv_text: str, jd_text: str, **kwargs: Any) -> tuple[CVData, JobDescription]:
        """Extract structured data from raw CV and Job Description text.

        Returns:
            Tuple of (CVData, JobDescription).
        """
        user_prompt = f"CV Text:\n```\n{cv_text}\n```\n\nJob Description Text:\n```\n{jd_text}\n```"

        raw = self._call_llm(user_prompt, system_prompt=SYSTEM_PROMPT)
        data = self._parse_json(raw)

        cv_data = CVData.safe_parse(data.get("cv", {}))
        jd_data = JobDescription.safe_parse(data.get("job_description", {}))

        logger.info(
            "extraction_completed",
            agent=self.agent_name,
            candidate_name=cv_data.personal.name,
        )
        return cv_data, jd_data
