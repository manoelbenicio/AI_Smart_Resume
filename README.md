# Executive Competitive Landscape Benchmark Engine

**Smart AI Resume** — A multi-agent Python system that evaluates executive CVs against target job descriptions, scores market positioning across 8 dimensions, benchmarks against executive archetypes, and generates repositioned, ATS-friendly CVs.

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
- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys) (GPT-4o)

### 1. Clone & Install

```bash
cd d:\VMs\Projetos\Smart_AI_Resume

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
```

### 3. Run via CLI

```bash
smart-resume analyze --cv tests/fixtures/sample_cv.txt --jd tests/fixtures/sample_jd.txt
```

### 4. Run via API

```bash
uvicorn smart_resume.api.app:app --reload --port 8000
# then open http://localhost:8000/docs for Swagger UI
```

---

## Project Structure

```
Smart_AI_Resume/
├── src/smart_resume/
│   ├── agents/           # 7 specialized LLM agents
│   │   ├── base.py           BaseAgent (provider-agnostic LLM abstraction)
│   │   ├── extraction.py     Phase 1 — CV + JD parsing
│   │   ├── scoring.py        Phase 2 — 8-category market positioning
│   │   ├── benchmark.py      Phase 3 — Executive archetype comparison
│   │   ├── distinctiveness.py Phase 4 — Differentiators
│   │   ├── risk_assessment.py Phase 5 — Risk classification
│   │   ├── cv_generator.py   Phase 6 — CV rewrite
│   │   └── re_evaluation.py  Phase 7 — Score & iterate
│   ├── models/           # Pydantic v2 data models
│   ├── parsers/          # DOCX / PDF / URL ingestion
│   ├── exporters/        # DOCX / PDF output generation
│   ├── api/              # FastAPI REST API
│   ├── orchestrator.py   # 8-phase pipeline sequencer
│   ├── cli.py            # Typer CLI entry point
│   └── config.py         # Settings via pydantic-settings
├── tests/
│   ├── fixtures/         # Sample CV + JD for testing
│   ├── unit/             # Model, parser, config tests
│   └── integration/      # Full pipeline tests
├── docs/
│   ├── AGENTS_LOG.md     # Timestamped execution audit log
│   ├── DELIVERABLES.md   # Feature contract tracking
│   └── ARCHITECTURE.md   # System design documentation
├── outputs/              # Runtime outputs (gitignored)
├── CHANGELOG.md          # Version history
└── pyproject.toml        # Python project config
```

---

## Testing

```bash
# Run all tests
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

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/analyze` | Upload CV + JD, run full pipeline |
| `GET` | `/api/v1/runs/{run_id}` | Retrieve past run results |
| `GET` | `/api/v1/runs/{run_id}/download` | Download final DOCX |

---

## License

Proprietary — All rights reserved.
