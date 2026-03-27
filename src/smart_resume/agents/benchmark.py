"""Phase 3 — Benchmark Agent: Compare candidate to executive archetypes."""

from __future__ import annotations

from typing import Any

import structlog

from smart_resume.agents.base import BaseAgent
from smart_resume.models.scores import BenchmarkResult

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
You are a Benchmark Agent comparing an executive to various archetypes.

Steps:
1. Use the candidate's structured data and category scores to evaluate their performance \
against typical leaders in:
   - Fortune 100
   - Big Tech
   - Tier-1 consulting
   - IPO/M&A-focused companies
   - Global executives (multi-region responsibilities).
2. Classify the candidate for each archetype as "Below Average", "Average", \
"Above Average", "Top 10%", or "Top 1%".
3. Provide a rationale for each classification based on scale, complexity, \
transformation impact, financial results and international exposure.
4. Return valid JSON with keys: "benchmark" and "rationales".
"""


class BenchmarkAgent(BaseAgent):
    """Compare candidate to 5 executive archetypes."""

    agent_name = "BenchmarkAgent"

    def run(self, *, candidate_json: str, scores_json: str, **kwargs: Any) -> BenchmarkResult:
        """Benchmark the candidate against Fortune 100, Big Tech, Consulting, IPO/M&A, Global.

        Returns:
            BenchmarkResult with classifications and rationales.
        """
        user_prompt = (
            f"Candidate Data:\n```\n{candidate_json}\n```\n\n"
            f"Category Scores:\n```\n{scores_json}\n```"
        )

        raw = self._call_llm(user_prompt, system_prompt=SYSTEM_PROMPT)
        data = self._parse_json(raw)

        result = BenchmarkResult.safe_parse(data)
        logger.info(
            "benchmark_completed",
            agent=self.agent_name,
            archetype_count=len(result.benchmark),
        )
        return result
