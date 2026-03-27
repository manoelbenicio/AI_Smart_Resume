"""API request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request body for the analyze endpoint (text-based input)."""

    cv_text: str = Field(..., description="Raw CV text")
    jd_text: str = Field(..., description="Raw JD text or URL")


class AnalyzeResponse(BaseModel):
    """Simplified response for the analyze endpoint."""

    run_id: str
    final_score: float
    iterations_used: int
    overall_positioning_score: float | None = None
    benchmark: dict[str, str] | None = None
    differentiators: list[str] | None = None
    weaknesses: list[str] | None = None
    risks: dict[str, dict[str, str]] | None = None
    improved_cv_markdown: str = ""
    output_docx_path: str | None = None
    output_pdf_path: str | None = None
