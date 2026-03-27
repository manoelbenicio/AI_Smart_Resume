"""Phase 7 — Re-Evaluation Agent: Score improved CV against Job Description."""

from __future__ import annotations

import logging
from typing import Any

from smart_resume.agents.base import BaseAgent
from smart_resume.models.scores import ReEvaluationResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a Re-Evaluation Agent comparing the updated CV to the job description.

Use this weighted rubric (total 100):
- 35: Critical requirement coverage (skills, scope, leadership expectations)
- 25: Scale and strategic experience alignment (team size, budget, global scope, M&A)
- 20: Quantifiable outcomes (real metrics or explicit placeholders)
- 10: Executive narrative and board readiness
- 10: ATS keyword and cultural-fit alignment

Scoring rules:
1. Count clearly labeled placeholders as valid coverage when they directly address \
missing quantifiable requirements from the JD.
2. If all critical JD requirements are explicitly addressed (with evidence or precise \
placeholders), score MUST be >= 90.
3. Score below 90 only if one or more critical requirements are not addressed at all.

Output rules:
- Return valid JSON with keys: "score", "explanation", "recommendations".
- Keep explanation concise and evidence-based.
- If score < 90, recommendations must be specific missing requirements with the exact \
placeholder to insert (e.g., **[MOCK_GLOBAL_REVENUE_GROWTH]**).
"""


class ReEvaluationAgent(BaseAgent):
    """Score the improved CV against the Job Description and recommend improvements."""

    agent_name = "ReEvaluationAgent"

    def run(self, *, improved_cv_markdown: str, job_json: str, **kwargs: Any) -> ReEvaluationResult:
        """Evaluate improved CV alignment with job description.

        Returns:
            ReEvaluationResult with score, explanation, and recommendations.
        """
        user_prompt = (
            f"Improved CV Markdown:\n```\n{improved_cv_markdown}\n```\n\n"
            f"Job Data:\n```\n{job_json}\n```"
        )

        raw = self._call_llm(user_prompt, system_prompt=SYSTEM_PROMPT)
        data = self._parse_json(raw)

        result = ReEvaluationResult.model_validate(data)
        logger.info("[%s] Score: %.1f | Recommendations: %d", self.agent_name, result.score, len(result.recommendations))
        return result
