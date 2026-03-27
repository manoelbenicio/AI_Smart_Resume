"""Pipeline state and audit trail model."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from smart_resume.models.cv import CVData
from smart_resume.models.job import JobDescription
from smart_resume.models.risk import DistinctivenessResult, RiskAssessment
from smart_resume.models.scores import BenchmarkResult, ReEvaluationResult, ScoringResult


class PipelineRun(BaseModel):
    """Complete state for a single orchestrator run — serves as the audit trail."""

    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str | None = None

    # ─── Inputs ───
    cv_source: str = ""  # original filename or "text"
    jd_source: str = ""  # original text, filename, or URL
    raw_cv_text: str = ""
    raw_jd_text: str = ""

    # ─── Phase Outputs ───
    extraction_cv: CVData | None = None
    extraction_jd: JobDescription | None = None
    scoring: ScoringResult | None = None
    benchmark: BenchmarkResult | None = None
    distinctiveness: DistinctivenessResult | None = None
    risk_assessment: RiskAssessment | None = None
    improved_cv_markdown: str = ""
    re_evaluation: ReEvaluationResult | None = None
    re_evaluation_history: list[ReEvaluationResult] = Field(default_factory=list)

    # ─── Final ───
    final_score: float = 0
    iterations_used: int = 0
    output_docx_path: str | None = None
    output_pdf_path: str | None = None
