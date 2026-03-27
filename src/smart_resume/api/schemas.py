"""API request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request body for the analyze endpoint (text-based input)."""

    cv_text: str = Field(..., description="Raw CV text")
    jd_text: str = Field("", description="Raw JD text (optional)")
    job_url: str = Field("", description="URL of target job posting (optional)")
    job_title: str = Field("", description="Target job title (optional)")
    strict_mode: bool = Field(False, description="Apply stricter scoring")


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


class RegisterRequest(BaseModel):
    """Auth register request payload."""

    email: str
    password: str
    full_name: str | None = None


class RegisterResponse(BaseModel):
    """Auth register response payload."""

    user_id: str
    email: str


class LoginRequest(BaseModel):
    """Auth login request payload."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response payload."""

    access_token: str
    token_type: str = "bearer"


class RunSummaryResponse(BaseModel):
    """Lightweight pipeline run summary for listing."""

    run_id: str
    final_score: float
    iterations_used: int
    created_at: str | None = None
