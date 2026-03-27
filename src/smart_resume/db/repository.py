"""Repository helpers for persisted pipeline runs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_resume.db.models import PipelineRunRecord, UserRecord
from smart_resume.models.pipeline import PipelineRun


def _parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse ISO datetime strings emitted by pipeline state."""
    if value is None:
        return None
    return datetime.fromisoformat(value)


def _strip_nul_chars(value: Any) -> Any:
    """Recursively remove NUL characters from JSON-compatible payloads."""
    if isinstance(value, str):
        return value.replace("\x00", "")
    if isinstance(value, list):
        return [_strip_nul_chars(item) for item in value]
    if isinstance(value, dict):
        return {key: _strip_nul_chars(item) for key, item in value.items()}
    return value


async def _ensure_user_for_run(session: AsyncSession, user_id: str) -> None:
    """Ensure the run owner exists to satisfy FK constraints."""
    existing = await session.get(UserRecord, user_id)
    if existing is not None:
        return

    if user_id != "anonymous":
        raise ValueError(f"User {user_id} not found")

    session.add(
        UserRecord(
            id="anonymous",
            email="local@dev",
            hashed_password="__disabled__",
            full_name="Local Anonymous",
            is_active=True,
        )
    )
    await session.flush()


async def save_run(session: AsyncSession, user_id: str, pipeline_run: PipelineRun) -> PipelineRunRecord:
    """Persist a pipeline run payload and summary metadata."""
    await _ensure_user_for_run(session, user_id)
    payload = _strip_nul_chars(pipeline_run.model_dump(mode="json"))

    record = await session.get(PipelineRunRecord, pipeline_run.run_id)
    if record is None:
        record = PipelineRunRecord(
            id=pipeline_run.run_id,
            user_id=user_id,
            started_at=_parse_iso_datetime(pipeline_run.started_at) or datetime.utcnow(),
            completed_at=_parse_iso_datetime(pipeline_run.completed_at),
            final_score=float(pipeline_run.final_score),
            iterations_used=int(pipeline_run.iterations_used),
            data=payload,
            output_docx_path=pipeline_run.output_docx_path,
            output_pdf_path=pipeline_run.output_pdf_path,
        )
        session.add(record)
    else:
        record.user_id = user_id
        record.started_at = _parse_iso_datetime(pipeline_run.started_at) or record.started_at
        record.completed_at = _parse_iso_datetime(pipeline_run.completed_at)
        record.final_score = float(pipeline_run.final_score)
        record.iterations_used = int(pipeline_run.iterations_used)
        record.data = payload
        record.output_docx_path = pipeline_run.output_docx_path
        record.output_pdf_path = pipeline_run.output_pdf_path

    await session.commit()
    await session.refresh(record)
    return record


async def get_run(session: AsyncSession, run_id: str) -> PipelineRunRecord | None:
    """Fetch a single run by id."""
    return await session.get(PipelineRunRecord, run_id)


async def list_runs(session: AsyncSession, user_id: str, limit: int = 20) -> list[PipelineRunRecord]:
    """List most recent runs for a user."""
    result = await session.scalars(
        select(PipelineRunRecord)
        .where(PipelineRunRecord.user_id == user_id)
        .order_by(PipelineRunRecord.created_at.desc())
        .limit(limit)
    )
    return list(result.all())
