"""Phase 2 — Scoring Agent: Market Positioning Score across 8 weighted categories."""

from __future__ import annotations

from typing import Any

import structlog

from smart_resume.agents.base import BaseAgent
from smart_resume.models.scores import ScoringResult

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
You are a Market Positioning Scoring Agent evaluating executives against top performers \
in Fortune 500, Big Tech and Tier-1 consulting.

Steps:
1. Review the candidate's structured data and the job description requirements.
2. Assign a score (0-100) for each of the following categories:
   - Scale of operations (budget, headcount, regions) – weight 20%
   - Strategic Complexity of initiatives – weight 15%
   - Transformation History (number and impact of transformations led) – weight 15%
   - Competitive Differentiation (unique skills or innovations) – weight 15%
   - International Experience – weight 10%
   - Career Progression Speed – weight 10%
   - Financial Impact (savings, revenue growth, ROI) – weight 10%
   - Executive Presence & Branding – weight 5%
3. Provide a brief justification for each category score, citing specific achievements \
or metrics from the candidate's data.
4. Calculate a weighted overall score (0-100) using the weights specified.
5. Return valid JSON with keys: "category_scores", "overall_score", "explanations".
"""


class ScoringAgent(BaseAgent):
    """Evaluate candidate market positioning across 8 weighted categories."""

    agent_name = "ScoringAgent"

    def run(self, *, candidate_json: str, job_json: str, **kwargs: Any) -> ScoringResult:
        """Score the candidate across 8 categories and compute weighted overall score.

        Args:
            candidate_json: Serialised CVData JSON.
            job_json: Serialised JobDescription JSON.

        Returns:
            ScoringResult with category scores, overall score, and explanations.
        """
        user_prompt = (
            f"Candidate Data:\n```\n{candidate_json}\n```\n\n"
            f"Job Data:\n```\n{job_json}\n```"
        )

        raw = self._call_llm(user_prompt, system_prompt=SYSTEM_PROMPT)
        data = self._parse_json(raw)

        result = ScoringResult.safe_parse(data)
        logger.info(
            "scoring_completed",
            agent=self.agent_name,
            overall_score=result.overall_score,
        )
        return result
