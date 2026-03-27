"""Phase 6 — CV Generator Agent: Produce repositioned ATS-friendly Markdown CV."""

from __future__ import annotations

import logging
from typing import Any

from smart_resume.agents.base import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a Premium CV Generator Agent tasked with repositioning a senior executive's résumé.

Primary objective: produce a CV likely to score >= 90 in re-evaluation.

Non-negotiable rules:
1. Rewrite the CV using strategic, board-ready, value-creation language that highlights \
scale, complexity, global impact, transformation outcomes, and financial impact.
2. Cover every major job requirement from Job Data explicitly. If evidence exists, state it. \
If evidence is missing, add a bold placeholder in square brackets with a specific label \
(example: **[MOCK_LED_2000_PLUS_TECH_PROFESSIONALS]**).
3. Every impact bullet must include a measurable result (real metric or placeholder).
4. Avoid generic bullets. Use action + scope + measurable business result.

Required ATS-friendly structure:
- **Summary:** 2-3 sentences with strategic scope and enterprise impact.
- **Core Competencies:** role-relevant keywords from Job Data.
- **Professional Experience:** each role with 3-5 quantified bullets.
- **Executive Alignment Highlights:** bullets that directly map to critical JD requirements \
  (global scale, budget size, M&A, board governance, AI/cloud transformation, compliance, \
  industry relevance, thought leadership).
- **Education & Certifications**
- **Skills & Languages**

Output format:
- Markdown CV only.
- After the CV, add `---` and one short justification paragraph explaining how the rewrite \
  closes requirement gaps and increases market positioning.
"""


class CVGeneratorAgent(BaseAgent):
    """Generate a repositioned executive CV in Markdown format."""

    agent_name = "CVGeneratorAgent"

    def run(
        self,
        *,
        candidate_json: str,
        distinctiveness_json: str,
        risks_json: str,
        job_json: str,
        recommendations: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate (or revise) the improved CV Markdown.

        Args:
            candidate_json: Serialised CVData.
            distinctiveness_json: Serialised DistinctivenessResult.
            risks_json: Serialised RiskAssessment.
            job_json: Serialised JobDescription.
            recommendations: Optional re-evaluation recommendations for revision pass.

        Returns:
            Improved CV as a Markdown string (includes justification after ---).
        """
        parts = [
            f"Candidate Data:\n```\n{candidate_json}\n```",
            f"Distinctiveness Data:\n```\n{distinctiveness_json}\n```",
            f"Risk Data:\n```\n{risks_json}\n```",
            f"Job Data:\n```\n{job_json}\n```",
        ]

        if recommendations:
            recs_text = "\n".join(f"- {r}" for r in recommendations)
            parts.append(
                f"\n**REVISION REQUIRED — address these gaps from the Re-Evaluation Agent:**\n{recs_text}\n"
                "Treat every recommendation as mandatory. Add an explicit bullet in "
                "`Executive Alignment Highlights` for each unresolved gap and use clear bold "
                "placeholders (e.g., **[MOCK_GLOBAL_REVENUE_GROWTH]**) where factual metrics are missing."
            )

        user_prompt = "\n\n".join(parts)
        raw = self._call_llm(user_prompt, system_prompt=SYSTEM_PROMPT)

        logger.info("[%s] Generated CV — %d chars", self.agent_name, len(raw))
        return raw
