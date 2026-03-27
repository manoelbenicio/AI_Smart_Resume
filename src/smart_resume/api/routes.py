"""API routes — REST endpoints for the Executive CV Benchmark Engine."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from smart_resume.api.schemas import AnalyzeRequest, AnalyzeResponse
from smart_resume.orchestrator import Orchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["pipeline"])

# In-memory store for completed runs (v1 — replace with DB later)
_runs: dict[str, object] = {}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the full 8-phase pipeline with text inputs."""
    orchestrator = Orchestrator()
    state = orchestrator.run(cv_input=request.cv_text, jd_input=request.jd_text)
    _runs[state.run_id] = state
    return _build_response(state)


@router.post("/analyze/upload", response_model=AnalyzeResponse)
async def analyze_upload(
    cv_file: UploadFile = File(..., description="CV file (docx/pdf/txt)"),
    jd_text: str = Form(..., description="Job description text or URL"),
) -> AnalyzeResponse:
    """Run the full pipeline with a file upload for the CV."""
    # Save uploaded file temporarily
    suffix = Path(cv_file.filename or "cv.txt").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await cv_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        orchestrator = Orchestrator()
        state = orchestrator.run(cv_input=tmp_path, jd_input=jd_text)
        _runs[state.run_id] = state
        return _build_response(state)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.get("/runs/{run_id}/download")
def download_cv(run_id: str, format: str = "docx") -> FileResponse:
    """Download the generated CV as DOCX or PDF."""
    state = _runs.get(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    if format == "pdf" and hasattr(state, "output_pdf_path") and state.output_pdf_path:  # type: ignore[union-attr]
        return FileResponse(state.output_pdf_path, media_type="application/pdf", filename="cv.pdf")  # type: ignore[union-attr]

    if hasattr(state, "output_docx_path") and state.output_docx_path:  # type: ignore[union-attr]
        return FileResponse(
            state.output_docx_path,  # type: ignore[union-attr]
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="cv.docx",
        )

    raise HTTPException(status_code=404, detail="No output file found for this run")


def _build_response(state: object) -> AnalyzeResponse:
    """Build API response from pipeline state."""
    from smart_resume.models.pipeline import PipelineRun

    assert isinstance(state, PipelineRun)

    risks_dict = None
    if state.risk_assessment:
        risks_dict = {k: {"level": v.level, "explanation": v.explanation} for k, v in state.risk_assessment.risks.items()}

    return AnalyzeResponse(
        run_id=state.run_id,
        final_score=state.final_score,
        iterations_used=state.iterations_used,
        overall_positioning_score=state.scoring.overall_score if state.scoring else None,
        benchmark=state.benchmark.benchmark if state.benchmark else None,
        differentiators=state.distinctiveness.differentiators if state.distinctiveness else None,
        weaknesses=state.distinctiveness.weaknesses if state.distinctiveness else None,
        risks=risks_dict,
        improved_cv_markdown=state.improved_cv_markdown,
        output_docx_path=state.output_docx_path,
        output_pdf_path=state.output_pdf_path,
    )
