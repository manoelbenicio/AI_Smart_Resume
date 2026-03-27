# Executive Competitive Landscape Benchmark Engine

**Smart AI Resume** — A multi-agent Python system that evaluates executive CVs against target job descriptions, scores market positioning across 8 dimensions, benchmarks against executive archetypes, and generates repositioned, ATS-friendly CVs.

**Version:** 0.4.0 | **Tests:** 53/53 | **GitHub:** [manoelbenicio/AI_Smart_Resume](https://github.com/manoelbenicio/AI_Smart_Resume)

---

## Architecture

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
                                                              Audit Trail JSON
```

**8-Phase Pipeline:**
1. **Extraction** — Parse CV + JD into structured Pydantic models
2. **Scoring** — Rate across 8 weighted categories (Scale, Strategic Complexity, Impact, etc.)
3. **Benchmark** — Compare against Fortune 100 CTO, Big Tech VP, PE Portfolio archetypes
4. **Distinctiveness** — Identify differentiators vs. commodity traits
5. **Risk Assessment** — Flag gaps (scale, international, board, innovation, digital)
6. **CV Generation** — Rewrite CV as ATS-friendly Markdown
7. **Re-Evaluation** — Score the rewritten CV; if < 90, loop back to Phase 6
8. **Export** — Produce styled DOCX + PDF + full audit trail JSON

---

## Quick Start

### Prerequisites
- Python 3.11+ and Docker Desktop
- An [OpenAI API key](https://platform.openai.com/api-keys) (GPT-4o)

### 1. Clone & Install

```bash
git clone https://github.com/manoelbenicio/AI_Smart_Resume.git
cd AI_Smart_Resume

# Create virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

# Install all dependencies
pip install -e ".[dev]"
```

### 2. Configure

```bash
copy .env.example .env
# Edit .env and add your OpenAI API key:
#   OPENAI_API_KEY=sk-...
#   JWT_SECRET_KEY=your-secret-here
#   DATABASE_URL=postgresql+asyncpg://smartresume:smartresume@localhost:5432/smartresume
```

### 3. Start Database

```bash
docker compose up -d postgres
# Run migrations
alembic upgrade head
```

### 4. Run via CLI

```bash
smart-resume analyze --cv tests/fixtures/sample_cv.txt --jd tests/fixtures/sample_jd.txt
```

### 5. Run via API

```bash
uvicorn smart_resume.api.app:app --reload --port 8000
# then open http://localhost:8000/docs for Swagger UI
```

### 6. Run Frontend

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

---

## Project Structure

```
Smart_AI_Resume/
├── src/smart_resume/
│   ├── agents/           # 7 specialized LLM agents
│   ├── models/           # Pydantic v2 data models (LLMSafeModel)
│   ├── parsers/          # DOCX / PDF / URL ingestion
│   ├── exporters/        # DOCX / PDF output generation
│   ├── api/              # FastAPI REST API + JWT auth
│   │   ├── auth.py           JWT helpers + get_current_user
│   │   ├── auth_routes.py    POST /auth/register, /auth/login
│   │   ├── routes.py         Pipeline endpoints (protected)
│   │   └── schemas.py        Request/response models
│   ├── db/               # Async SQLAlchemy persistence
│   │   ├── engine.py         Async engine + sessions
│   │   ├── models.py         UserRecord, PipelineRunRecord
│   │   ├── repository.py     save_run, get_run, list_runs
│   │   └── migrations/       Alembic (users + pipeline_runs)
│   ├── orchestrator.py   # 8-phase pipeline sequencer
│   ├── cli.py            # Typer CLI entry point
│   └── config.py         # Settings via pydantic-settings
├── frontend/             # Premium Next.js 15 dashboard
│   ├── app/              # App Router pages
│   ├── components/       # ScoreHero, RadarChart, BenchmarkBars, RiskHeatmap
│   └── lib/              # API client, types
├── tests/
│   ├── fixtures/         # Sample CV + JD for testing
│   ├── unit/             # Model, parser, config, auth, repository tests
│   └── integration/      # Full pipeline tests
├── docs/                 # Project management docs
├── outputs/              # Runtime outputs (gitignored)
├── CHANGELOG.md          # Version history
├── docker-compose.yml    # API + PostgreSQL services
└── pyproject.toml        # Python project config
```

---

## Testing

```bash
# Run all tests (53 tests)
python -m pytest tests/ -v --tb=short

# With coverage
python -m pytest tests/ -v --cov=smart_resume --cov-report=term-missing

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | OpenAI API key |
| `LLM_MODEL` | `gpt-4o` | Model for agent calls |
| `TARGET_SCORE` | `90` | Minimum re-evaluation score |
| `MAX_REEVAL_ITERATIONS` | `3` | Max retry loops |
| `OUTPUT_DIR` | `outputs` | Directory for results |
| `LOG_LEVEL` | `INFO` | Logging level |
| `AUTH_ENABLED` | `true` | JWT authentication toggle |
| `JWT_SECRET_KEY` | *(required)* | Secret for JWT signing |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async database URL |

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | No | Register new user |
| `POST` | `/api/v1/auth/login` | No | Login, receive JWT |
| `POST` | `/api/v1/analyze` | JWT | Upload CV + JD, run full pipeline |
| `POST` | `/api/v1/analyze/upload` | JWT | File upload variant |
| `GET` | `/api/v1/runs` | JWT | List user's pipeline runs |
| `GET` | `/api/v1/runs/{run_id}/download` | JWT | Download final DOCX |
| `GET` | `/health` | No | Health check |

---

## Docker

```bash
# Start everything (API + PostgreSQL)
docker compose up -d

# Just the database
docker compose up -d postgres

# Rebuild API container
docker compose up -d --build smart-resume-api
```

---

## License

Proprietary — All rights reserved.
