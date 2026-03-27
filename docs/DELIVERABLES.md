# Deliverables Contract

Maps every requirement from `project_scope.md` to implementation status.

| # | Feature | Source | File(s) | Status |
|---|---|---|---|---|
| 1 | CV structured extraction (JSON) | Scope §Extraction | `agents/extraction.py`, `models/cv.py` | ✅ Done |
| 2 | JD structured extraction (JSON) | Scope §Extraction | `agents/extraction.py`, `models/job.py` | ✅ Done |
| 3 | Market Positioning Score (8 categories) | Scope §Scoring | `agents/scoring.py`, `models/scores.py` | ✅ Done |
| 4 | 8 weighted categories (20/15/15/15/10/10/10/5) | Scope §Scoring | `agents/scoring.py` | ✅ Done |
| 5 | Executive archetype benchmark | Scope §Benchmark | `agents/benchmark.py`, `models/scores.py` | ✅ Done |
| 6 | 5 archetype tiers | Scope §Benchmark | `agents/benchmark.py` | ✅ Done |
| 7 | Distinctiveness assessment | Scope §Distinctiveness | `agents/distinctiveness.py`, `models/risk.py` | ✅ Done |
| 8 | 3 differentiators + commodity check | Scope §Distinctiveness | `agents/distinctiveness.py` | ✅ Done |
| 9 | 5-category risk assessment | Scope §Risk | `agents/risk_assessment.py`, `models/risk.py` | ✅ Done |
| 10 | Risk levels (Low/Medium/High/Critical) | Scope §Risk | `agents/risk_assessment.py` | ✅ Done |
| 11 | ATS-friendly CV generation | Scope §CV Generator | `agents/cv_generator.py` | ✅ Done |
| 12 | Re-evaluation with target score | Scope §Re-Evaluation | `agents/re_evaluation.py` | ✅ Done |
| 13 | Retry loop (Phase 7→6 if < 90) | Scope §Orchestrator | `orchestrator.py` | ✅ Done |
| 14 | 8-phase pipeline sequencing | Scope §Pipeline | `orchestrator.py` | ✅ Done |
| 15 | DOCX ingestion | Scope §Input | `parsers/docx_parser.py` | ✅ Done |
| 16 | PDF ingestion | Scope §Input | `parsers/pdf_parser.py` | ✅ Done |
| 17 | URL-based JD extraction | Scope §Input | `parsers/url_parser.py` | ✅ Done |
| 18 | DOCX export (styled) | Scope §Output | `exporters/docx_exporter.py` | ✅ Done |
| 19 | PDF export | Scope §Output | `exporters/pdf_exporter.py` | ✅ Done |
| 20 | CLI interface | Scope §Interface | `cli.py` | ✅ Done |
| 21 | REST API (FastAPI) | Scope §Interface | `api/app.py`, `api/routes.py`, `api/schemas.py` | ✅ Done |
| 22 | Audit trail JSON persistence | Scope §Audit | `models/pipeline.py`, `orchestrator.py` | ✅ Done |
| 23 | Configuration via env vars | Scope §Config | `config.py`, `.env.example` | ✅ Done |
| 24 | Unit tests | Scope §QA | `tests/unit/` (17 tests) | ✅ Done |
| 25 | Integration tests | Scope §QA | `tests/integration/` (12 tests) | ✅ Done |
| 26 | README documentation | Scope §Docs | `README.md` | ✅ Done |
| 27 | Architecture documentation | Scope §Docs | `docs/ARCHITECTURE.md` | ✅ Done |
| 28 | Streamlit UI | Scope §Stretch | `src/smart_resume/ui/app.py` | ✅ Done |
| 29 | LLM output hardening (LLMSafeModel) | Post-testing | `models/base.py`, all model files | ✅ Done |
| 30 | Verified E2E pipeline run (8 phases, score 85.0) | Post-testing | `outputs/`, audit trail JSON | ✅ Done |
| 31 | Professional handover document | Project Governance | `docs/HANDOVER.md` | ✅ Done |
| 32 | Agentic communication protocol | Project Governance | `docs/AGENTIC_PROTOCOL.md` | ✅ Done |
| 33 | CLI category score display hotfix (8 non-zero scores rendered) | Handover §6.1 | `src/smart_resume/cli.py`, `src/smart_resume/models/scores.py` | ✅ Done |
| 34 | LLMSafeModel edge-case unit test suite (41 total tests) | Handover §6.2 | `tests/unit/test_edge_cases.py` | ✅ Done |
| 35 | Prompt tuning to achieve score >= 90 in <= 3 iterations | Handover §6.3 | `src/smart_resume/agents/cv_generator.py`, `src/smart_resume/agents/re_evaluation.py` | ✅ Done |
| 36 | Docker containerization and Compose runtime validation | Handover §6.4 | `Dockerfile`, `docker-compose.yml`, `.dockerignore` | ✅ Done |
| 37 | GitHub Actions CI workflow (pytest + ruff + mypy) | Handover §6.5 | `.github/workflows/ci.yml` | ✅ Done |
| 38 | Streamlit UI runtime validation at localhost:8501 | Handover §6.6 | `src/smart_resume/ui/app.py`, `pyproject.toml` | ✅ Done |
