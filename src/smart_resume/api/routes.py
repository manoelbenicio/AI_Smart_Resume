"""API routes — REST endpoints for the Executive CV Benchmark Engine."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from smart_resume.api.auth import UserContext, get_current_user
from smart_resume.api.schemas import AnalyzeRequest, AnalyzeResponse, RunSummaryResponse
from smart_resume.db.engine import get_db
from smart_resume.db.repository import get_run, list_runs as list_runs_for_user, save_run
from smart_resume.orchestrator import Orchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["pipeline"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    """Run the full 8-phase pipeline with text inputs."""
    effective_jd = request.jd_text
    if request.job_url:
        url_context = f"[Target Job URL: {request.job_url}]"
        effective_jd = f"{url_context}\n\n{request.jd_text}" if request.jd_text else url_context
    if request.job_title and not effective_jd:
        effective_jd = f"Target role: {request.job_title}"

    orchestrator = Orchestrator()
    state = await run_in_threadpool(orchestrator.run, request.cv_text, effective_jd)
    await save_run(db, user.user_id, state)
    return _build_response(state)


@router.post("/analyze/upload", response_model=AnalyzeResponse)
async def analyze_upload(
    cv_file: UploadFile = File(..., description="CV file (docx/pdf/txt)"),
    jd_text: str = Form("", description="Job description text"),
    job_url: str = Form("", description="URL of target job posting"),
    job_title: str = Form("", description="Target job title"),
    strict_mode: bool = Form(False, description="Apply stricter scoring"),
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    """Run the full pipeline with a file upload for the CV."""
    # Combine JD text with job URL context if both provided
    effective_jd = jd_text
    if job_url:
        url_context = f"[Target Job URL: {job_url}]"
        effective_jd = f"{url_context}\n\n{jd_text}" if jd_text else url_context
    if job_title and not effective_jd:
        effective_jd = f"Target role: {job_title}"

    # Save uploaded file temporarily
    suffix = Path(cv_file.filename or "cv.txt").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await cv_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        orchestrator = Orchestrator()
        state = await run_in_threadpool(orchestrator.run, tmp_path, effective_jd)
        await save_run(db, user.user_id, state)
        return _build_response(state)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.get("/runs/{run_id}/download")
async def download_cv(
    run_id: str,
    format: str = "docx",
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download the generated CV as DOCX or PDF."""
    run_record = await get_run(db, run_id)
    if not run_record:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    if run_record.user_id != user.user_id:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    if format == "pdf" and run_record.output_pdf_path:
        return FileResponse(run_record.output_pdf_path, media_type="application/pdf", filename="cv.pdf")

    if run_record.output_docx_path:
        return FileResponse(
            run_record.output_docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="cv.docx",
        )

    raise HTTPException(status_code=404, detail="No output file found for this run")


@router.get("/runs", response_model=list[RunSummaryResponse])
async def list_runs(
    user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[RunSummaryResponse]:
    """List all run summaries for the current user."""
    records = await list_runs_for_user(db, user.user_id)
    return [
        RunSummaryResponse(
            run_id=record.id,
            final_score=record.final_score,
            iterations_used=record.iterations_used,
            created_at=record.created_at.isoformat() if record.created_at else None,
        )
        for record in records
    ]


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
