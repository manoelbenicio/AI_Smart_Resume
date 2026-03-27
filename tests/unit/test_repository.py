"""Unit tests for async pipeline run repository."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from smart_resume.db.base import Base
from smart_resume.db.models import UserRecord
from smart_resume.db.repository import get_run, list_runs, save_run
from smart_resume.models.pipeline import PipelineRun


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Yield an isolated async DB session with schema created."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as db_session:
        yield db_session

    await engine.dispose()


async def _create_user(session: AsyncSession, user_id: str, email: str) -> None:
    session.add(
        UserRecord(
            id=user_id,
            email=email,
            hashed_password="__test_hash__",
            full_name="Test User",
            is_active=True,
        )
    )
    await session.commit()


def _build_pipeline_run(run_id: str, final_score: float = 0) -> PipelineRun:
    return PipelineRun(
        run_id=run_id,
        started_at="2026-03-26T23:10:00",
        completed_at="2026-03-26T23:15:00",
        final_score=final_score,
        iterations_used=2,
        improved_cv_markdown="## Improved CV",
        output_docx_path=f"outputs/{run_id}/cv.docx",
        output_pdf_path=f"outputs/{run_id}/cv.pdf",
    )


@pytest.mark.asyncio
async def test_save_run_persists_pipeline_metadata(session: AsyncSession) -> None:
    await _create_user(session, "user-1", "user1@test.com")
    state = _build_pipeline_run("run-1", final_score=91.0)

    record = await save_run(session, "user-1", state)

    assert record.id == "run-1"
    assert record.user_id == "user-1"
    assert record.final_score == 91.0
    assert record.iterations_used == 2
    assert record.output_docx_path == "outputs/run-1/cv.docx"
    assert record.data["run_id"] == "run-1"


@pytest.mark.asyncio
async def test_get_run_returns_none_for_unknown_id(session: AsyncSession) -> None:
    result = await get_run(session, "missing-run")
    assert result is None


@pytest.mark.asyncio
async def test_list_runs_filters_by_user(session: AsyncSession) -> None:
    await _create_user(session, "user-a", "a@test.com")
    await _create_user(session, "user-b", "b@test.com")
    await save_run(session, "user-a", _build_pipeline_run("run-a1", 88.0))
    await save_run(session, "user-b", _build_pipeline_run("run-b1", 77.0))
    await save_run(session, "user-a", _build_pipeline_run("run-a2", 93.0))

    runs = await list_runs(session, "user-a", limit=20)
    run_ids = {record.id for record in runs}

    assert run_ids == {"run-a1", "run-a2"}


@pytest.mark.asyncio
async def test_save_run_updates_existing_record(session: AsyncSession) -> None:
    await _create_user(session, "user-1", "user1@test.com")
    await save_run(session, "user-1", _build_pipeline_run("run-1", final_score=70.0))
    updated_state = _build_pipeline_run("run-1", final_score=95.0)
    updated_state.iterations_used = 3

    await save_run(session, "user-1", updated_state)
    stored = await get_run(session, "run-1")

    assert stored is not None
    assert stored.final_score == 95.0
    assert stored.iterations_used == 3


@pytest.mark.asyncio
async def test_save_run_strips_nul_characters_from_payload(session: AsyncSession) -> None:
    await _create_user(session, "user-1", "user1@test.com")
    state = _build_pipeline_run("run-null", final_score=81.0)
    state.improved_cv_markdown = "Header\x00Body"

    record = await save_run(session, "user-1", state)

    def contains_nul(value: object) -> bool:
        if isinstance(value, str):
            return "\x00" in value
        if isinstance(value, list):
            return any(contains_nul(item) for item in value)
        if isinstance(value, dict):
            return any(contains_nul(item) for item in value.values())
        return False

    assert not contains_nul(record.data)
