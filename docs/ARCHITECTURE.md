# Architecture — Executive Benchmark Engine (v0.4.0)

> **Updated:** 2026-03-27 | **Agent:** Antigravity

---

## System Architecture Overview

```
                    ┌──────────────────────────────────────────────────────────────┐
                    │                     Docker Compose                          │
                    │                                                              │
  ┌──────────┐     │  ┌────────────────────────────────────────────────────────┐  │
  │ Next.js  │     │  │                  FastAPI (smart-resume-api)            │  │
  │ Frontend │────▶│  │                                                        │  │
  │ :3000    │ API │  │  ┌─────────┐   ┌──────────────┐   ┌──────────────┐   │  │
  └──────────┘     │  │  │  Auth   │   │  Pipeline    │   │ Orchestrator │   │  │
                   │  │  │ Routes  │   │   Routes     │   │  (8-Phase)   │   │  │
                   │  │  └────┬────┘   └──────┬───────┘   └──────┬───────┘   │  │
                   │  │       │               │                   │           │  │
                   │  │       ▼               ▼                   ▼           │  │
                   │  │  ┌─────────────────────────────────────────────┐      │  │
                   │  │  │         Async SQLAlchemy (db layer)         │      │  │
                   │  │  │  engine.py │ models.py │ repository.py     │      │  │
                   │  │  └──────────────────┬──────────────────────────┘      │  │
                   │  └─────────────────────┼──────────────────────────────────┘  │
                   │                        ▼                                     │
                   │  ┌──────────────────────────────────────────────────────────┐│
                   │  │            PostgreSQL 16 (postgres:5432)                 ││
                   │  │  Tables: users │ pipeline_runs (JSONB)                  ││
                   │  └──────────────────────────────────────────────────────────┘│
                   └──────────────────────────────────────────────────────────────┘
```

---

## 8-Phase Pipeline Data Flow

```
CV (DOCX/PDF/TXT)  ──┐
                      ├──► Extraction Agent ──► Scoring Agent ──► Benchmark Agent
JD (Text/URL)     ──┘          │                     │                  │
                               ▼                     ▼                  ▼
                         Distinctiveness ──► Risk Assessment ──► CV Generator ──► Re-Evaluation
                            Agent              Agent              Agent            Agent
                                                                    │                │
                                                                    │  score < 90    │
                                                                    ◄────────────────┘
                                                                    │  score ≥ 90
                                                                    ▼
                                                              DOCX/PDF Export
                                                              Audit Trail (DB + JSON)
```

| Phase | Agent | Input | Output |
|-------|-------|-------|--------|
| 1 | Extraction | Raw CV + JD text | `CVData` + `JobDescription` |
| 2 | Scoring | Structured CV + JD | `ScoringResult` (8 categories) |
| 3 | Benchmark | Scoring result | `BenchmarkResult` (5 archetypes) |
| 4 | Distinctiveness | All prior context | Differentiators + commodity check |
| 5 | Risk Assessment | All prior context | 5-category risk matrix |
| 6 | CV Generator | All analysis + JD | ATS-friendly CV (Markdown) |
| 7 | Re-Evaluation | Generated CV + JD | Score → if < 90, retry Phase 6 |
| 8 | Export | Final CV | Styled DOCX + PDF + audit trail |

---

## Authentication Layer

```
POST /auth/register  ──► hash_password (bcrypt) ──► INSERT INTO users
POST /auth/login     ──► verify_password ──► create_access_token (JWT HS256)
Protected routes     ──► get_current_user(Bearer token) ──► UserContext
```

- **Toggle:** `AUTH_ENABLED=false` bypasses JWT validation → returns `anonymous/local@dev`.
- **Tokens:** Signed with `JWT_SECRET_KEY`, expire after `jwt_expire_minutes` (default 1440 = 24h).
- **Scope:** Every `PipelineRun` is tagged with `user_id` for multi-tenant isolation.

---

## Database Schema

```sql
-- Managed via Alembic migrations (src/smart_resume/db/migrations/)

CREATE TABLE users (
    id          VARCHAR PRIMARY KEY,   -- UUID
    email       VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name   VARCHAR,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE pipeline_runs (
    id              VARCHAR PRIMARY KEY,   -- run UUID
    user_id         VARCHAR NOT NULL REFERENCES users(id),
    started_at      TIMESTAMP NOT NULL,
    completed_at    TIMESTAMP,
    final_score     FLOAT DEFAULT 0,
    iterations_used INTEGER DEFAULT 0,
    data            JSONB NOT NULL,        -- full PipelineRun.model_dump()
    output_docx_path VARCHAR,
    output_pdf_path  VARCHAR,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

**Design decision:** Full `PipelineRun` state stored as JSONB for schema flexibility. Indexed metadata columns (`user_id`, `final_score`, `created_at`) enable efficient queries without denormalizing nested structures.

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| LLM Provider | OpenAI via `openai` SDK | Best structured output support; abstracted via `BaseAgent` |
| Data validation | Pydantic v2 + `LLMSafeModel` | Type-safe with automatic null→[], int→str coercion for LLM output |
| API framework | FastAPI (async) | Async-native, auto OpenAPI docs, file upload support |
| CLI framework | Typer | Built on Click; type-annotated, auto-generates help |
| Authentication | Self-hosted JWT (`python-jose` + `passlib`) | 100% portable — no external auth services required |
| Database | PostgreSQL 16 (async via `asyncpg`) | JSONB for flexible pipeline state, ACID for auth |
| ORM | SQLAlchemy 2.0 (async) + Alembic | Industry standard, async session support, migration management |
| Frontend | Next.js 15 + Tailwind CSS v4 + Recharts | Premium dashboard with radar charts, heatmaps, animated scores |
| Containerization | Docker Compose | Single `docker compose up` for API + PostgreSQL + CLI |
| State management | PostgreSQL (primary) + JSON fallback | DB persistence survives restarts; JSON backup for auditing |
| CI/CD | GitHub Actions | Automated pytest + ruff + mypy on push/PR to `main` |

---

## API Surface

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Create user account |
| `POST` | `/api/v1/auth/login` | Public | Authenticate, receive JWT |
| `POST` | `/api/v1/analyze` | JWT | Analyze CV+JD (text input) |
| `POST` | `/api/v1/analyze/upload` | JWT | Analyze CV+JD (file upload) |
| `GET` | `/api/v1/runs` | JWT | List user's pipeline runs |
| `GET` | `/api/v1/runs/{id}/download` | JWT | Download generated DOCX |
| `GET` | `/health` | Public | Service health check |

---

## File Structure

```
Smart_AI_Resume/
├── src/smart_resume/
│   ├── agents/           # 7 specialized LLM agents (BaseAgent pattern)
│   ├── models/           # Pydantic v2 models (LLMSafeModel base class)
│   ├── parsers/          # DOCX / PDF / URL ingestion
│   ├── exporters/        # DOCX / PDF output generation
│   ├── api/
│   │   ├── app.py            FastAPI app factory + CORS
│   │   ├── auth.py           JWT helpers + get_current_user dependency
│   │   ├── auth_routes.py    POST /auth/register, /auth/login
│   │   ├── routes.py         Pipeline endpoints (protected by JWT)
│   │   └── schemas.py        Request/response Pydantic models
│   ├── db/
│   │   ├── engine.py         Async SQLAlchemy engine + session factory
│   │   ├── base.py           Declarative base for ORM models
│   │   ├── models.py         UserRecord, PipelineRunRecord
│   │   ├── repository.py     save_run, get_run, list_runs
│   │   └── migrations/       Alembic (2 migrations: users + pipeline_runs)
│   ├── ui/               # (Superseded) Streamlit prototype
│   ├── orchestrator.py   # 8-phase pipeline sequencer
│   ├── cli.py            # Typer CLI entry point
│   └── config.py         # pydantic-settings configuration
├── frontend/             # Premium Next.js 15 dashboard
│   ├── app/              # App Router pages + layouts
│   ├── components/       # ScoreHero, RadarChart, BenchmarkBars, RiskHeatmap
│   └── lib/              # API client, TypeScript types
├── tests/                # 53 tests (unit + integration)
├── docs/                 # Project governance + handover docs
├── scripts/              # Docker fix scripts (Windows)
├── docker-compose.yml    # API + PostgreSQL + CLI services
├── Dockerfile            # Multi-stage Python 3.12 build
└── .github/workflows/    # CI pipeline (pytest + ruff + mypy)
```
