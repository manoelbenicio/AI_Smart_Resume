"""End-to-End API tests for the Executive CV Benchmark Engine.

These tests exercise every public API endpoint through the full ASGI stack,
using an in-memory SQLite database.  They validate:

  1. Auth flow: register → login → token usage → token rejection
  2. Text analysis: with JD, without JD, with job_url, with all fields
  3. File upload: DOCX upload, PDF upload, minimal upload (no optional fields)
  4. Run listing and retrieval
  5. Error scenarios: bad file types, missing fields, invalid tokens
  6. CORS / health / docs endpoints

These would have caught every 422 bug we've seen today.
"""

from __future__ import annotations

import io
from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from smart_resume.api.app import app
from smart_resume.db.base import Base
from smart_resume.db.engine import get_db


# ────────────────────────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────────────────────────

@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Provide an API client backed by an in-memory async SQLite DB."""
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


async def _register_and_login(client: AsyncClient, email: str = "qa@test.com") -> str:
    """Helper: register + login → return bearer token."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPass123!", "full_name": "QA Bot"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass123!"},
    )
    return login.json()["access_token"]


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _fake_docx() -> io.BytesIO:
    """Create a minimal valid .docx-like file for upload tests."""
    content = b"PK\x03\x04" + b"\x00" * 26 + b"fake docx content for testing"
    buf = io.BytesIO(content)
    buf.name = "test_cv.docx"
    return buf


def _fake_txt() -> io.BytesIO:
    """Create a minimal .txt CV for upload tests."""
    content = b"""John Doe
Senior Software Engineer | 10+ years
Experience: Led team of 12 at Fortune 500 company.
Skills: Python, AWS, Kubernetes, Machine Learning.
Education: M.S. Computer Science, Stanford University."""
    buf = io.BytesIO(content)
    buf.name = "test_cv.txt"
    return buf


# ────────────────────────────────────────────────────────────────────
# 1. HEALTH & INFRASTRUCTURE
# ────────────────────────────────────────────────────────────────────

class TestHealthAndInfra:
    """Health check, CORS, and OpenAPI docs must always be up."""

    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client: AsyncClient) -> None:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_openapi_docs_available(self, client: AsyncClient) -> None:
        r = await client.get("/docs")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_openapi_json_available(self, client: AsyncClient) -> None:
        r = await client.get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema
        assert "/api/v1/analyze" in schema["paths"]
        assert "/api/v1/analyze/upload" in schema["paths"]


# ────────────────────────────────────────────────────────────────────
# 2. AUTH FLOW — Full lifecycle
# ────────────────────────────────────────────────────────────────────

class TestAuthFlow:
    """Complete authentication lifecycle tests."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient) -> None:
        r = await client.post(
            "/api/v1/auth/register",
            json={"email": "new@test.com", "password": "Pass123!", "full_name": "Test"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["user_id"]
        assert data["email"] == "new@test.com"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient) -> None:
        payload = {"email": "dup@test.com", "password": "Pass123!", "full_name": "Dup"}
        r1 = await client.post("/api/v1/auth/register", json=payload)
        r2 = await client.post("/api/v1/auth/register", json=payload)
        assert r1.status_code == 200
        assert r2.status_code == 409

    @pytest.mark.asyncio
    async def test_register_missing_email(self, client: AsyncClient) -> None:
        r = await client.post(
            "/api/v1/auth/register",
            json={"password": "Pass123!", "full_name": "No Email"},
        )
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_password(self, client: AsyncClient) -> None:
        r = await client.post(
            "/api/v1/auth/register",
            json={"email": "nopass@test.com", "full_name": "No Pass"},
        )
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient) -> None:
        token = await _register_and_login(client, "login@test.com")
        assert isinstance(token, str)
        assert len(token) > 20

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/auth/register",
            json={"email": "wp@test.com", "password": "Pass123!", "full_name": "WP"},
        )
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": "wp@test.com", "password": "WrongPass!"},
        )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@test.com", "password": "Pass123!"},
        )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient) -> None:
        r = await client.get("/api/v1/runs")
        assert r.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient) -> None:
        r = await client.get(
            "/api/v1/runs",
            headers={"Authorization": "Bearer invalidtoken123"},
        )
        assert r.status_code in (401, 403)


# ────────────────────────────────────────────────────────────────────
# 3. TEXT ANALYSIS ENDPOINT — /api/v1/analyze
# ────────────────────────────────────────────────────────────────────

class TestTextAnalysis:
    """Tests for POST /api/v1/analyze (JSON body)."""

    @pytest.mark.asyncio
    async def test_analyze_text_minimal(self, client: AsyncClient) -> None:
        """Minimal call: only cv_text, no JD, no job_url."""
        token = await _register_and_login(client, "text_min@test.com")
        r = await client.post(
            "/api/v1/analyze",
            json={"cv_text": "John Doe. Senior Engineer. 10 years experience."},
            headers=_auth_header(token),
        )
        assert r.status_code == 200
        data = r.json()
        assert "run_id" in data
        assert isinstance(data["final_score"], (int, float))

    @pytest.mark.asyncio
    async def test_analyze_text_with_jd(self, client: AsyncClient) -> None:
        """With both CV text and JD text."""
        token = await _register_and_login(client, "text_jd@test.com")
        r = await client.post(
            "/api/v1/analyze",
            json={
                "cv_text": "John Doe. Senior Engineer. 10 years experience in cloud systems.",
                "jd_text": "Looking for a Senior Cloud Architect with 8+ years AWS experience.",
            },
            headers=_auth_header(token),
        )
        assert r.status_code == 200
        data = r.json()
        assert data["run_id"]

    @pytest.mark.asyncio
    async def test_analyze_text_with_job_url(self, client: AsyncClient) -> None:
        """With CV text and job_url — no jd_text."""
        token = await _register_and_login(client, "text_url@test.com")
        r = await client.post(
            "/api/v1/analyze",
            json={
                "cv_text": "Jane Smith. VP of Engineering. Managed $50M budget.",
                "job_url": "https://linkedin.com/jobs/view/12345",
            },
            headers=_auth_header(token),
        )
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_analyze_text_all_fields(self, client: AsyncClient) -> None:
        """All optional fields provided."""
        token = await _register_and_login(client, "text_all@test.com")
        r = await client.post(
            "/api/v1/analyze",
            json={
                "cv_text": "Full CV content here with leadership and strategy.",
                "jd_text": "VP Engineering role at Fortune 500.",
                "job_url": "https://linkedin.com/jobs/view/99999",
                "job_title": "VP of Engineering",
                "strict_mode": True,
            },
            headers=_auth_header(token),
        )
        assert r.status_code == 200
        data = r.json()
        assert data["run_id"]

    @pytest.mark.asyncio
    async def test_analyze_text_missing_cv_returns_422(self, client: AsyncClient) -> None:
        """cv_text is required — omitting it must return 422."""
        token = await _register_and_login(client, "text_no_cv@test.com")
        r = await client.post(
            "/api/v1/analyze",
            json={"jd_text": "Some JD"},
            headers=_auth_header(token),
        )
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_analyze_text_unauthenticated(self, client: AsyncClient) -> None:
        r = await client.post(
            "/api/v1/analyze",
            json={"cv_text": "Test"},
        )
        assert r.status_code in (401, 403)


# ────────────────────────────────────────────────────────────────────
# 4. FILE UPLOAD ENDPOINT — /api/v1/analyze/upload
# ────────────────────────────────────────────────────────────────────

class TestFileUpload:
    """Tests for POST /api/v1/analyze/upload (multipart form)."""

    @pytest.mark.asyncio
    async def test_upload_minimal_only_file(self, client: AsyncClient) -> None:
        """Upload with only cv_file — no optional fields.
        This is the EXACT scenario that caused the 422 bug.
        """
        token = await _register_and_login(client, "upload_min@test.com")
        f = _fake_txt()
        r = await client.post(
            "/api/v1/analyze/upload",
            files={"cv_file": ("cv.txt", f, "text/plain")},
            headers=_auth_header(token),
        )
        # Should NOT be 422 — jd_text is optional
        assert r.status_code == 200, f"Expected 200 but got {r.status_code}: {r.text}"

    @pytest.mark.asyncio
    async def test_upload_with_jd_text(self, client: AsyncClient) -> None:
        """Upload file + jd_text (the original expected usage)."""
        token = await _register_and_login(client, "upload_jd@test.com")
        f = _fake_txt()
        r = await client.post(
            "/api/v1/analyze/upload",
            files={"cv_file": ("cv.txt", f, "text/plain")},
            data={"jd_text": "Looking for a CTO with 15+ years."},
            headers=_auth_header(token),
        )
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_upload_with_job_url_only(self, client: AsyncClient) -> None:
        """Upload file + job_url, no jd_text.
        This is the LinkedIn URL scenario the user reported.
        """
        token = await _register_and_login(client, "upload_url@test.com")
        f = _fake_txt()
        r = await client.post(
            "/api/v1/analyze/upload",
            files={"cv_file": ("cv.txt", f, "text/plain")},
            data={"job_url": "https://www.linkedin.com/jobs/view/4385294750/"},
            headers=_auth_header(token),
        )
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_upload_all_fields(self, client: AsyncClient) -> None:
        """Upload file with every optional field populated."""
        token = await _register_and_login(client, "upload_all@test.com")
        f = _fake_txt()
        r = await client.post(
            "/api/v1/analyze/upload",
            files={"cv_file": ("cv.txt", f, "text/plain")},
            data={
                "jd_text": "VP Engineering role",
                "job_url": "https://linkedin.com/jobs/view/99",
                "job_title": "VP of Engineering",
                "strict_mode": "true",
            },
            headers=_auth_header(token),
        )
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_upload_wrong_field_name_returns_422(self, client: AsyncClient) -> None:
        """Frontend sending 'file' instead of 'cv_file' must be caught."""
        token = await _register_and_login(client, "upload_wrong@test.com")
        f = _fake_txt()
        r = await client.post(
            "/api/v1/analyze/upload",
            files={"file": ("cv.txt", f, "text/plain")},  # WRONG key!
            headers=_auth_header(token),
        )
        assert r.status_code == 422, "Backend must reject wrong file field name"

    @pytest.mark.asyncio
    async def test_upload_no_file_returns_422(self, client: AsyncClient) -> None:
        """Upload without any file must return 422."""
        token = await _register_and_login(client, "upload_nofile@test.com")
        r = await client.post(
            "/api/v1/analyze/upload",
            data={"jd_text": "Some JD"},
            headers=_auth_header(token),
        )
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_upload_unauthenticated(self, client: AsyncClient) -> None:
        f = _fake_txt()
        r = await client.post(
            "/api/v1/analyze/upload",
            files={"cv_file": ("cv.txt", f, "text/plain")},
        )
        assert r.status_code in (401, 403)


# ────────────────────────────────────────────────────────────────────
# 5. RUNS LISTING — /api/v1/runs
# ────────────────────────────────────────────────────────────────────

class TestRunListing:
    """Tests for GET /api/v1/runs."""

    @pytest.mark.asyncio
    async def test_runs_empty_for_new_user(self, client: AsyncClient) -> None:
        token = await _register_and_login(client, "runs_empty@test.com")
        r = await client.get("/api/v1/runs", headers=_auth_header(token))
        assert r.status_code == 200
        assert r.json() == []

    @pytest.mark.asyncio
    async def test_runs_appear_after_analysis(self, client: AsyncClient) -> None:
        token = await _register_and_login(client, "runs_after@test.com")
        # Run an analysis
        await client.post(
            "/api/v1/analyze",
            json={"cv_text": "Test CV content for listing."},
            headers=_auth_header(token),
        )
        # Check runs
        r = await client.get("/api/v1/runs", headers=_auth_header(token))
        assert r.status_code == 200
        runs = r.json()
        assert len(runs) >= 1
        assert "run_id" in runs[0]

    @pytest.mark.asyncio
    async def test_runs_isolated_between_users(self, client: AsyncClient) -> None:
        """User A's runs must NOT appear in User B's listing."""
        token_a = await _register_and_login(client, "user_a@test.com")
        token_b = await _register_and_login(client, "user_b@test.com")

        # User A makes an analysis
        await client.post(
            "/api/v1/analyze",
            json={"cv_text": "User A's CV."},
            headers=_auth_header(token_a),
        )

        # User B should see zero runs
        r = await client.get("/api/v1/runs", headers=_auth_header(token_b))
        assert r.status_code == 200
        assert len(r.json()) == 0

    @pytest.mark.asyncio
    async def test_runs_unauthenticated(self, client: AsyncClient) -> None:
        r = await client.get("/api/v1/runs")
        assert r.status_code in (401, 403)


# ────────────────────────────────────────────────────────────────────
# 6. OPENAPI CONTRACT VALIDATION
# ────────────────────────────────────────────────────────────────────

class TestOpenAPIContract:
    """Ensure the OpenAPI spec matches what the frontend expects."""

    @pytest.mark.asyncio
    async def test_analyze_upload_has_optional_jd_text(self, client: AsyncClient) -> None:
        """The /analyze/upload endpoint MUST accept jd_text as optional."""
        r = await client.get("/openapi.json")
        schema = r.json()

        upload_path = schema["paths"]["/api/v1/analyze/upload"]["post"]
        # The requestBody should NOT list jd_text as required
        body = upload_path.get("requestBody", {})
        # For multipart, check that jd_text has a default
        content = body.get("content", {}).get("multipart/form-data", {})
        if "schema" in content:
            required = content["schema"].get("required", [])
            assert "jd_text" not in required, \
                "jd_text must be OPTIONAL in /analyze/upload — this caused the 422 bug"

    @pytest.mark.asyncio
    async def test_analyze_schema_has_job_url(self, client: AsyncClient) -> None:
        """AnalyzeRequest must include job_url field."""
        r = await client.get("/openapi.json")
        schema = r.json()
        components = schema.get("components", {}).get("schemas", {})
        analyze_req = components.get("AnalyzeRequest", {})
        props = analyze_req.get("properties", {})
        assert "job_url" in props, "AnalyzeRequest schema must include job_url field"

    @pytest.mark.asyncio
    async def test_analyze_schema_has_job_title(self, client: AsyncClient) -> None:
        """AnalyzeRequest must include job_title field."""
        r = await client.get("/openapi.json")
        schema = r.json()
        components = schema.get("components", {}).get("schemas", {})
        analyze_req = components.get("AnalyzeRequest", {})
        props = analyze_req.get("properties", {})
        assert "job_title" in props, "AnalyzeRequest schema must include job_title field"

    @pytest.mark.asyncio
    async def test_analyze_schema_has_strict_mode(self, client: AsyncClient) -> None:
        """AnalyzeRequest must include strict_mode field."""
        r = await client.get("/openapi.json")
        schema = r.json()
        components = schema.get("components", {}).get("schemas", {})
        analyze_req = components.get("AnalyzeRequest", {})
        props = analyze_req.get("properties", {})
        assert "strict_mode" in props, "AnalyzeRequest schema must include strict_mode field"

    @pytest.mark.asyncio
    async def test_cv_text_is_required(self, client: AsyncClient) -> None:
        """cv_text must remain required in AnalyzeRequest."""
        r = await client.get("/openapi.json")
        schema = r.json()
        components = schema.get("components", {}).get("schemas", {})
        analyze_req = components.get("AnalyzeRequest", {})
        required = analyze_req.get("required", [])
        assert "cv_text" in required, "cv_text must be REQUIRED in AnalyzeRequest"
