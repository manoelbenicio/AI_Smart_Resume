"""Phase 5 — Risk Assessment Agent: Classify positioning risks by severity."""

from __future__ import annotations

import logging
from typing import Any

from smart_resume.agents.base import BaseAgent
from smart_resume.models.risk import RiskAssessment

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a Risk Assessment Agent identifying positioning risks for executives.

Steps:
1. Assess the candidate's profile to determine if they lack scale, international \
exposure, financial impact, strategic narrative or if they present an excessively \
operational background.
2. For each risk category (scale, international_exposure, financial_impact, \
strategic_narrative, operational_bias), assign a severity level: "Low", "Medium", \
"High", or "Critical".
3. Provide a brief explanation for each severity level, referencing the candidate's \
achievements or missing data.
4. Return valid JSON with a single key "risks" containing objects with "level" and \
"explanation" for each category.
"""


class RiskAssessmentAgent(BaseAgent):
    """Evaluate positioning risks across 5 categories."""

    agent_name = "RiskAssessmentAgent"

    def run(self, *, candidate_json: str, **kwargs: Any) -> RiskAssessment:
        """Assess 5 risk categories and assign severity levels.

        Returns:
            RiskAssessment with risk items.
        """
        user_prompt = f"Candidate Data:\n```\n{candidate_json}\n```"

        raw = self._call_llm(user_prompt, system_prompt=SYSTEM_PROMPT)
        data = self._parse_json(raw)

        result = RiskAssessment.model_validate(data)
        high_risks = [k for k, v in result.risks.items() if v.level in ("High", "Critical")]
        logger.info("[%s] High/Critical risks: %s", self.agent_name, high_risks or "None")
        return result
