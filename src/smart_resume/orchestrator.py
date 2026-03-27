"""Orchestrator — 8-phase pipeline sequencer with retry logic and audit trail."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from smart_resume.agents.benchmark import BenchmarkAgent
from smart_resume.agents.cv_generator import CVGeneratorAgent
from smart_resume.agents.distinctiveness import DistinctivenessAgent
from smart_resume.agents.extraction import ExtractionAgent
from smart_resume.agents.re_evaluation import ReEvaluationAgent
from smart_resume.agents.risk_assessment import RiskAssessmentAgent
from smart_resume.agents.scoring import ScoringAgent
from smart_resume.config import settings
from smart_resume.exporters.docx_exporter import export_docx
from smart_resume.exporters.pdf_exporter import export_pdf
from smart_resume.models.pipeline import PipelineRun
from smart_resume.parsers.docx_parser import parse_docx
from smart_resume.parsers.pdf_parser import parse_pdf

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates the 8-phase executive CV benchmark pipeline.

    Phases:
        1. Extraction   — CV + JD → structured JSON
        2. Scoring       — Market Positioning (8 weighted categories)
        3. Benchmark     — Executive archetype comparison
        4. Distinctiveness — Differentiators + commodity assessment
        5. Risk Assessment — 5 risk categories
        6. CV Generation  — Repositioned ATS-friendly Markdown CV
        7. Re-Evaluation  — Score ≥ target_score loop
        8. Export          — DOCX (+ optional PDF)
    """

    def __init__(self) -> None:
        self.extraction = ExtractionAgent()
        self.scoring = ScoringAgent()
        self.benchmark = BenchmarkAgent()
        self.distinctiveness = DistinctivenessAgent()
        self.risk_assessment = RiskAssessmentAgent()
        self.cv_generator = CVGeneratorAgent()
        self.re_evaluation = ReEvaluationAgent()

    def run(self, cv_input: str, jd_input: str) -> PipelineRun:
        """Execute the full 8-phase pipeline.

        Args:
            cv_input: Path to CV file (docx/pdf/txt) OR raw text.
            jd_input: Raw JD text, path to file, or URL (http:// prefix).

        Returns:
            PipelineRun with all phase outputs and audit trail.
        """
        state = PipelineRun()

        # ─── Resolve CV input ───
        cv_text = self._resolve_cv(cv_input)
        state.raw_cv_text = cv_text
        state.cv_source = cv_input

        # ─── Resolve JD input ───
        jd_text = self._resolve_jd(jd_input)
        state.raw_jd_text = jd_text
        state.jd_source = jd_input

        # ─── Phase 1: Extraction ───
        logger.info("═══ Phase 1: Extraction ═══")
        cv_data, jd_data = self.extraction.run(cv_text=cv_text, jd_text=jd_text)
        state.extraction_cv = cv_data
        state.extraction_jd = jd_data

        candidate_json = cv_data.model_dump_json(indent=2)
        job_json = jd_data.model_dump_json(indent=2)

        # ─── Phase 2: Scoring ───
        logger.info("═══ Phase 2: Scoring ═══")
        state.scoring = self.scoring.run(candidate_json=candidate_json, job_json=job_json)
        scores_json = state.scoring.model_dump_json(indent=2)

        # ─── Phase 3: Benchmark ───
        logger.info("═══ Phase 3: Benchmark ═══")
        state.benchmark = self.benchmark.run(candidate_json=candidate_json, scores_json=scores_json)

        # ─── Phase 4: Distinctiveness ───
        logger.info("═══ Phase 4: Distinctiveness ═══")
        state.distinctiveness = self.distinctiveness.run(candidate_json=candidate_json, scores_json=scores_json)
        distinctiveness_json = state.distinctiveness.model_dump_json(indent=2)

        # ─── Phase 5: Risk Assessment ───
        logger.info("═══ Phase 5: Risk Assessment ═══")
        state.risk_assessment = self.risk_assessment.run(candidate_json=candidate_json)
        risks_json = state.risk_assessment.model_dump_json(indent=2)

        # ─── Phase 6: CV Generation ───
        logger.info("═══ Phase 6: CV Generation ═══")
        state.improved_cv_markdown = self.cv_generator.run(
            candidate_json=candidate_json,
            distinctiveness_json=distinctiveness_json,
            risks_json=risks_json,
            job_json=job_json,
        )

        # ─── Phase 7: Re-Evaluation Loop ───
        recommendations: list[str] | None = None
        for iteration in range(1, settings.max_reeval_iterations + 1):
            logger.info("═══ Phase 7: Re-Evaluation (iteration %d) ═══", iteration)
            reeval = self.re_evaluation.run(
                improved_cv_markdown=state.improved_cv_markdown,
                job_json=job_json,
            )
            state.re_evaluation = reeval
            state.re_evaluation_history.append(reeval)
            state.iterations_used = iteration

            if reeval.score >= settings.target_score:
                logger.info("✓ Score %.1f ≥ %d — CV accepted!", reeval.score, settings.target_score)
                break

            logger.info(
                "✗ Score %.1f < %d — revising CV (recommendations: %d)",
                reeval.score,
                settings.target_score,
                len(reeval.recommendations),
            )
            recommendations = reeval.recommendations

            # ─── Revision pass (back to Phase 6) ───
            state.improved_cv_markdown = self.cv_generator.run(
                candidate_json=candidate_json,
                distinctiveness_json=distinctiveness_json,
                risks_json=risks_json,
                job_json=job_json,
                recommendations=recommendations,
            )

        state.final_score = state.re_evaluation.score if state.re_evaluation else 0

        # ─── Phase 8: Export ───
        logger.info("═══ Phase 8: Export ═══")
        output_dir = settings.output_dir / state.run_id
        output_dir.mkdir(parents=True, exist_ok=True)

        docx_path = export_docx(state.improved_cv_markdown, output_dir / "cv.docx")
        state.output_docx_path = str(docx_path)

        pdf_path = export_pdf(state.improved_cv_markdown, output_dir / "cv.pdf")
        if pdf_path:
            state.output_pdf_path = str(pdf_path)

        # ─── Persist audit trail ───
        state.completed_at = datetime.now().isoformat()
        audit_path = output_dir / "pipeline_run.json"
        audit_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        logger.info("Audit trail saved to %s", audit_path)

        return state

    # ─── Input resolvers ─────────────────────────────────────────

    @staticmethod
    def _resolve_cv(cv_input: str) -> str:
        """Resolve CV input to raw text."""
        path = Path(cv_input)
        if path.exists():
            suffix = path.suffix.lower()
            if suffix == ".docx":
                return parse_docx(path)
            if suffix == ".pdf":
                return parse_pdf(path)
            return path.read_text(encoding="utf-8")
        # Treat as raw text
        return cv_input

    @staticmethod
    def _resolve_jd(jd_input: str) -> str:
        """Resolve JD input to raw text (file, URL, or raw text)."""
        if jd_input.startswith(("http://", "https://")):
            from smart_resume.parsers.url_parser import parse_url

            return parse_url(jd_input)
        path = Path(jd_input)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return jd_input
