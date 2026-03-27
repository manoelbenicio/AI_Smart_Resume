# CODEX BACKEND HANDOVER — Smart AI Resume

> **Handover Author:** Antigravity (Solutions Architect)
> **Handover Date:** 2026-03-26T23:17:00-03:00
> **Target Agent:** Codex
> **Project Root:** `d:\VMs\Projetos\Smart_AI_Resume`

---

## MANDATORY FIRST STEPS

1. Read `docs/AGENTIC_PROTOCOL.md` — you MUST follow all timestamped logging rules.
2. Read this handover in full before writing ANY code.
3. Read `docs/AGENTS_LOG.md` (last 5 entries) for continuity.
4. Add your onboarding entry to `docs/AGENTS_LOG.md` before writing ANY code.
5. Run `pytest tests/ -v --tb=short` to confirm baseline: **41/41 passing**.

---

## YOUR MISSION

You have **two tasks** to complete, in order:

| # | Task | ETA |
|---|------|-----|
| 1 | **User Authentication** — Self-hosted JWT auth with a `users` table in local Docker Postgres | 2 days |
| 2 | **DB Persistence** — Replace local JSON file persistence with PostgreSQL | 3 days |

> **IMPORTANT:** There are NO external cloud services (no Supabase, no Auth0, no Clerk).
> Everything runs 100% locally inside Docker Desktop. The same Postgres container
> serves both the `users` table (Task 1) and the `pipeline_runs` table (Task 2).

---

## TASK 1: User Authentication (Self-Hosted JWT + Local Postgres)

### Goal
Build a fully local authentication system:
- Users register and login via the FastAPI backend.
- Passwords are hashed with `bcrypt` and stored in a `users` table in the local Docker Postgres.
- Login returns a signed JWT. All pipeline endpoints require a valid `Bearer` token.
- Each `PipelineRun` is scoped to the authenticated `user_id`.

### Current State
- **No auth exists.** All endpoints are open.
- The in-memory `_runs` dict in `src/smart_resume/api/routes.py:19` is global and unscoped.
- The frontend at `frontend/` already calls `POST /api/v1/analyze` and `GET /api/v1/runs/{id}/download`.
- **No external services are used.** Keep it that way.

### Implementation Steps

#### 1.1 — Install Dependencies
Add to `pyproject.toml` `[project.dependencies]`:
```
"python-jose[cryptography]>=3.3.0",
"passlib[bcrypt]>=1.7.4",
"sqlalchemy[asyncio]>=2.0.30",
"asyncpg>=0.29.0",
"alembic>=1.13.0",
```

> **Note:** SQLAlchemy/asyncpg/Alembic are shared with Task 2. Install them now so
> the `users` table and `pipeline_runs` table share the same DB engine and migrations.

#### 1.2 — Add Environment Variables
Add to `.env.example` and `src/smart_resume/config.py` (`Settings` class):
```python
# ─── Auth ───
auth_enabled: bool = False                  # toggle: False = no auth required
jwt_secret_key: str = "change-me-in-production"  # used to sign/verify JWTs
jwt_algorithm: str = "HS256"
jwt_expire_minutes: int = 1440              # 24 hours

# ─── Database ───
database_url: str = "postgresql+asyncpg://smartuser:smartpass@localhost:5432/smart_resume"
db_echo: bool = False
```

#### 1.3 — Create Database Layer (shared with Task 2)
Create new directory: `src/smart_resume/db/`

**`db/__init__.py`** — empty.

**`db/engine.py`**:
- Create async SQLAlchemy engine from `settings.database_url`.
- Create `async_sessionmaker` for dependency injection.
- Provide `get_db()` async generator for FastAPI `Depends()`.

**`db/base.py`**:
- Define `Base = declarative_base()` — shared by all ORM models.

**`db/models.py`** — SQLAlchemy ORM tables:
```python
class UserRecord(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
```

#### 1.4 — Create Auth Module
Create new file: `src/smart_resume/api/auth.py`

This file must contain:

1. **`UserContext`** Pydantic model: `{ user_id: str, email: str }`.
2. **`hash_password(plain: str) -> str`** — uses `passlib.hash.bcrypt`.
3. **`verify_password(plain: str, hashed: str) -> bool`** — bcrypt verify.
4. **`create_access_token(data: dict) -> str`** — signs JWT with `jwt_secret_key`, adds `exp` claim.
5. **`get_current_user(token: str = Depends(oauth2_scheme)) -> UserContext`**:
   - Decodes the JWT using `python-jose`.
   - Extracts `sub` (user_id) and `email`.
   - Returns `UserContext`.
   - Raises `HTTPException(401)` if token is invalid/expired.
   - **When `settings.auth_enabled is False`**, skip validation and return `UserContext(user_id="anonymous", email="local@dev")`.

#### 1.5 — Create Auth Routes
Create new file: `src/smart_resume/api/auth_routes.py`

Two public endpoints (no auth required):

**`POST /api/v1/auth/register`**:
- Request body: `{ "email": str, "password": str, "full_name": str | None }`
- Hash the password, create `UserRecord` in DB.
- Return `{ "user_id": str, "email": str }`.
- Return `409 Conflict` if email already exists.

**`POST /api/v1/auth/login`**:
- Request body: `{ "email": str, "password": str }`
- Look up user by email, verify password.
- Return `{ "access_token": str, "token_type": "bearer" }`.
- Return `401` if credentials are invalid.

#### 1.6 — Protect Existing Routes
Modify `src/smart_resume/api/routes.py`:
- Add `user: UserContext = Depends(get_current_user)` to all three route handlers.
- Pass `user.user_id` into the response builder so runs are scoped.
- Add a new `GET /api/v1/runs` endpoint that lists all runs for the current user.

#### 1.7 — Register Routers
Modify `src/smart_resume/api/app.py`:
- Import and include `auth_routes.router`.

#### 1.8 — Docker Compose Postgres
Add to `docker-compose.yml` (will be reused by Task 2):
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: smart_resume
      POSTGRES_USER: smartuser
      POSTGRES_PASSWORD: smartpass
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

#### 1.9 — Alembic Setup
```bash
cd src/smart_resume
alembic init db/migrations
```
- Configure `alembic/env.py` to import `Base` and read `DATABASE_URL` from env.
- Generate initial migration: `alembic revision --autogenerate -m "create users table"`

### Acceptance Criteria
- [ ] `pytest tests/` still passes 41/41 (existing tests must NOT break).
- [ ] New unit tests for `auth.py` — minimum 5 tests:
  - Valid token → returns `UserContext`
  - Expired token → raises `401`
  - Missing token → raises `401`
  - `AUTH_ENABLED=False` → returns anonymous user without any token
  - Password hash + verify round-trip
- [ ] New unit tests for `auth_routes.py` — minimum 3 tests:
  - Register new user → `200`
  - Register duplicate email → `409`
  - Login with valid credentials → returns JWT
- [ ] `POST /api/v1/auth/register` creates a user in Postgres.
- [ ] `POST /api/v1/auth/login` returns a valid JWT.
- [ ] With `AUTH_ENABLED=False`, the pipeline API works exactly as before (no token needed).
- [ ] With `AUTH_ENABLED=True`, requests without a valid JWT return `401`.
- [ ] `docker-compose up postgres` starts the DB successfully.
- [ ] `alembic upgrade head` creates the `users` table.
- [ ] `docs/AGENTS_LOG.md` entry logged per protocol.
- [ ] `CHANGELOG.md` updated under a new version section.

---

## TASK 2: Pipeline Run Persistence (PostgreSQL — Same Local Docker DB)

### Goal
Replace the current in-memory store and JSON file persistence with the same local Docker Postgres database set up in Task 1. Pipeline runs must survive server restarts and be queryable by `user_id`.

> **Prerequisites from Task 1 (already done):**
> - `db/engine.py`, `db/base.py`, `db/models.py` exist.
> - `docker-compose.yml` has the `postgres` service.
> - Alembic is initialized.
> - SQLAlchemy/asyncpg/Alembic are already in `pyproject.toml`.
> - `database_url` is already in `config.py`.

### Current State — What You Are Replacing

**1. In-Memory Store** (`routes.py:19`):
```python
_runs: dict[str, object] = {}  # ← dies on server restart
```

**2. JSON File Persistence** (`orchestrator.py:156-160`):
```python
audit_path = output_dir / "pipeline_run.json"
audit_path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
```
Both must be replaced by DB writes.

**3. PipelineRun Model** (`models/pipeline.py`):
This Pydantic model has 15+ fields. Do NOT replicate every nested model as a separate table. Store the full `PipelineRun` as a JSONB column with indexed metadata columns for queries.

### Implementation Steps

#### 2.1 — Add PipelineRunRecord to `db/models.py`
Add to the existing `db/models.py` (which already has `UserRecord` from Task 1):
```python
class PipelineRunRecord(Base):
    __tablename__ = "pipeline_runs"

    id = Column(String, primary_key=True)           # run_id (UUID)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    final_score = Column(Float, default=0)
    iterations_used = Column(Integer, default=0)
    data = Column(JSONB, nullable=False)             # full PipelineRun.model_dump()
    output_docx_path = Column(String, nullable=True)
    output_pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
```

> **Note:** `user_id` has a `ForeignKey` to `users.id` (the table from Task 1).

#### 2.2 — Create Repository
Create new file: `src/smart_resume/db/repository.py`

CRUD functions:
- `save_run(session, user_id: str, pipeline_run: PipelineRun) -> PipelineRunRecord`
- `get_run(session, run_id: str) -> PipelineRunRecord | None`
- `list_runs(session, user_id: str, limit: int = 20) -> list[PipelineRunRecord]`

#### 2.3 — Generate Alembic Migration
```bash
alembic revision --autogenerate -m "create pipeline_runs table"
alembic upgrade head
```

#### 2.4 — Wire Into Routes
Modify `src/smart_resume/api/routes.py`:
- **Remove** the `_runs: dict[str, object] = {}` in-memory store entirely.
- Replace `_runs[state.run_id] = state` with `await repository.save_run(db, user.user_id, state)`.
- Replace `_runs.get(run_id)` with `await repository.get_run(db, run_id)`.
- The `GET /api/v1/runs` endpoint (added in Task 1) should now use `repository.list_runs()`.

#### 2.5 — Wire Into Orchestrator
Modify `src/smart_resume/orchestrator.py`:
- **Keep** the JSON file write (`pipeline_run.json`) as a local backup fallback.
- The DB persistence happens in the route handler, NOT inside the orchestrator.
- The orchestrator should NOT import any DB code — keep it a pure pipeline runner. The route handler is the glue.

### Acceptance Criteria
- [ ] `pytest tests/` still passes 41/41 + new auth tests from Task 1 (NO regressions).
- [ ] New unit tests for `repository.py` (save, get, list) — minimum 4 tests using SQLite in-memory.
- [ ] Alembic migration runs cleanly: `alembic upgrade head`.
- [ ] The `_runs` in-memory dict is **removed** from `routes.py`.
- [ ] Pipeline runs persist across API restarts (verified by restart test).
- [ ] `GET /api/v1/runs` returns the user's runs from the DB.
- [ ] `docs/AGENTS_LOG.md` entry logged per protocol.
- [ ] `CHANGELOG.md` updated.
- [ ] `docs/DELIVERABLES.md` updated (mark items 39–40 as Done).

---

## KEY FILES REFERENCE

| File | Purpose | Lines |
|------|---------|-------|
| `src/smart_resume/config.py` | Settings singleton (env vars) | 34 |
| `src/smart_resume/api/routes.py` | FastAPI endpoints (3 routes) | 96 |
| `src/smart_resume/api/schemas.py` | API request/response Pydantic models | 29 |
| `src/smart_resume/api/app.py` | FastAPI app factory + CORS | ~20 |
| `src/smart_resume/orchestrator.py` | 8-phase pipeline sequencer | 191 |
| `src/smart_resume/models/pipeline.py` | `PipelineRun` audit trail model | 45 |
| `pyproject.toml` | Dependencies and build config | 67 |
| `.env.example` | Environment variable template | 12 |
| `docker-compose.yml` | Container runtime services | ~20 |
| `tests/` | 41 tests (unit + integration) | ~400 |

---

## CONSTRAINTS & RULES

1. **Do NOT touch** `frontend/`, `agents/`, `models/`, `parsers/`, or `exporters/` — those are complete and stable.
2. **Do NOT break** the existing 41 tests. Run `pytest` after every change.
3. **All doc updates are MANDATORY** per `docs/AGENTIC_PROTOCOL.md`:
   - `docs/AGENTS_LOG.md` — timestamped entry per task.
   - `CHANGELOG.md` — new version section.
   - `docs/DELIVERABLES.md` — mark completed items.
4. Follow existing code style: type hints everywhere, docstrings, `ruff` clean.
5. Use **async** patterns for all DB operations (the FastAPI app is already async-capable).

---

## EXECUTION ORDER

```
Task 1 (Auth) MUST complete before Task 2 (DB Persistence)
because the DB schema needs user_id, which comes from auth.
```

1. ✅ Onboard — read docs, log entry.
2. ✅ Task 1 — Auth middleware, protect routes, add toggle, write tests.
3. ✅ Task 2 — DB layer, Alembic, wire routes, docker postgres, write tests.
4. ✅ Final — run full `pytest`, update all docs, report completion.
