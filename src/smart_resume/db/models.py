"""ORM models for backend persistence."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from smart_resume.db.base import Base

JSON_PAYLOAD_TYPE = JSON().with_variant(JSONB, "postgresql")


class UserRecord(Base):
    """Registered backend user."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class PipelineRunRecord(Base):
    """Persisted pipeline run scoped to a backend user."""

    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    final_score: Mapped[float] = mapped_column(Float, default=0)
    iterations_used: Mapped[int] = mapped_column(Integer, default=0)
    data: Mapped[dict[str, object]] = mapped_column(JSON_PAYLOAD_TYPE, nullable=False)
    output_docx_path: Mapped[str | None] = mapped_column(String, nullable=True)
    output_pdf_path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
