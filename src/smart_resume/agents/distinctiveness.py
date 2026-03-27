"""Phase 4 — Distinctiveness Agent: Identify differentiators, commodity status, weaknesses."""

from __future__ import annotations

from typing import Any

import structlog

from smart_resume.agents.base import BaseAgent
from smart_resume.models.risk import DistinctivenessResult

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
You are a Distinctiveness Agent assessing an executive's unique value.

Steps:
1. Review the candidate's structured data and category scores.
2. List three genuine differentiators (e.g., unmatched scale achievements, \
breakthrough transformations, multi-regional impact, visionary leadership).
3. Determine whether the candidate is a commodity (easily replaceable) or \
irreplaceable in the executive talent market.  Explain why.
4. Identify up to three weaknesses or gaps where stronger competitors might \
surpass them (e.g., limited board experience, weak financial impact, lack of global exposure).
5. Return valid JSON with keys: "differentiators", "is_commodity", \
"commodity_rationale", "weaknesses".
"""


class DistinctivenessAgent(BaseAgent):
    """Assess candidate's unique differentiators and potential weaknesses."""

    agent_name = "DistinctivenessAgent"

    def run(self, *, candidate_json: str, scores_json: str, **kwargs: Any) -> DistinctivenessResult:
        """Identify differentiators, commodity assessment, and weaknesses.

        Returns:
            DistinctivenessResult.
        """
        user_prompt = (
            f"Candidate Data:\n```\n{candidate_json}\n```\n\n"
            f"Scores:\n```\n{scores_json}\n```"
        )

        raw = self._call_llm(user_prompt, system_prompt=SYSTEM_PROMPT)
        data = self._parse_json(raw)

        result = DistinctivenessResult.safe_parse(data)
        logger.info(
            "distinctiveness_completed",
            agent=self.agent_name,
            is_commodity=result.is_commodity,
            differentiator_count=len(result.differentiators),
            weakness_count=len(result.weaknesses),
        )
        return result
