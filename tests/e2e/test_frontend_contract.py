"""Frontend-Backend Contract Tests.

These tests validate that the frontend's expected API contract matches
what the backend actually exposes.  They are the "canary in the coal mine"
for integration failures.

Key contracts verified:
  - Form field names match (cv_file, not file)
  - Optional fields are truly optional
  - Response shapes match frontend TypeScript interfaces
  - Content-Type expectations are correct
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from smart_resume.api.app import app
from smart_resume.db.base import Base
from smart_resume.db.engine import get_db


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()


class TestFrontendContract:
    """These tests mirror what the frontend Next.js code actually sends."""

    @pytest.mark.asyncio
    async def test_frontend_form_keys_match_backend(self, client: AsyncClient) -> None:
        """
        Frontend sends FormData with these keys:
          - cv_file (File)
          - jd_text (optional string)
          - job_url (optional string)
          - job_title (optional string)
          - strict_mode (optional string "true"/"false")

        Backend must accept ALL of these without 422.
        """
        # First register & login
        await client.post(
            "/api/v1/auth/register",
            json={"email": "contract@test.com", "password": "Pass123!", "full_name": "Contract"},
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": "contract@test.com", "password": "Pass123!"},
        )
        token = login.json()["access_token"]

        # Simulate EXACTLY what frontend/lib/api.ts sends
        import io
        cv = io.BytesIO(b"John Doe\nSenior Engineer\n10 years")
        cv.name = "resume.pdf"

        r = await client.post(
            "/api/v1/analyze/upload",
            files={"cv_file": ("resume.pdf", cv, "application/pdf")},
            data={
                "jd_text": "",  # Frontend sends empty string, not missing
                "job_url": "https://linkedin.com/jobs/view/123",
                "job_title": "CTO",
                "strict_mode": "false",  # Frontend sends string, not boolean
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200, \
            f"Frontend contract broken! {r.status_code}: {r.text}"

    @pytest.mark.asyncio
    async def test_frontend_minimal_upload(self, client: AsyncClient) -> None:
        """Frontend with NO optional fields filled in."""
        await client.post(
            "/api/v1/auth/register",
            json={"email": "minimal@test.com", "password": "Pass123!", "full_name": "Min"},
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": "minimal@test.com", "password": "Pass123!"},
        )
        token = login.json()["access_token"]

        import io
        cv = io.BytesIO(b"Jane Smith. VP Engineering.")
        r = await client.post(
            "/api/v1/analyze/upload",
            files={"cv_file": ("cv.docx", cv, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200, \
            f"Minimal upload broken! {r.status_code}: {r.text}"

    @pytest.mark.asyncio
    async def test_response_shape_matches_typescript(self, client: AsyncClient) -> None:
        """
        Frontend TypeScript expects AnalyzeResponse:
          { run_id: string, final_score: number, sections: [...], ... }
        """
        await client.post(
            "/api/v1/auth/register",
            json={"email": "shape@test.com", "password": "Pass123!", "full_name": "Shape"},
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": "shape@test.com", "password": "Pass123!"},
        )
        token = login.json()["access_token"]

        r = await client.post(
            "/api/v1/analyze",
            json={"cv_text": "Test CV for response shape validation."},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        data = r.json()

        # These fields MUST exist per frontend/lib/types.ts
        assert "run_id" in data, "response must contain run_id"
        assert "final_score" in data, "response must contain final_score"
        assert isinstance(data["final_score"], (int, float)), "final_score must be numeric"
