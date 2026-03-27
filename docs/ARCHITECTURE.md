# Architecture — Executive Benchmark Engine

## High-Level Data Flow

```
┌─────────────┐     ┌──────────────┐
│  CV (DOCX/  │────▶│   Parsers    │────▶ raw text
│  PDF/TXT)   │     └──────────────┘        │
└─────────────┘                             ▼
┌─────────────┐     ┌──────────────┐   ┌──────────────────┐
│  JD (text/  │────▶│  URL Parser  │──▶│  Extraction Agent │──▶ CVData + JobDescription (JSON)
│    URL)     │     └──────────────┘   └────────┬─────────┘
└─────────────┘                                 │
                                                ▼
                                   ┌────────────────────┐
                                   │  Scoring Agent      │──▶ CategoryScores + Overall
                                   └────────┬───────────┘
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                      ┌────────────┐ ┌────────────┐ ┌────────────┐
                      │ Benchmark  │ │Distinctive │ │   Risk     │
                      │   Agent    │ │   Agent    │ │   Agent    │
                      └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
                            │              │              │
                            └──────────────┼──────────────┘
                                           ▼
                                ┌──────────────────────┐
                                │  CV Generator Agent   │──▶ Improved CV (Markdown)
                                └────────┬─────────────┘
                                         │
                                         ▼
                                ┌──────────────────────┐
                                │ Re-Evaluation Agent   │──▶ Score ≥ 90? ──▶ Export
                                └────────┬─────────────┘         │
                                         │ score < 90            │
                                         └───────────────────────┘
                                           (retry loop, max 3x)
```

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| LLM Provider | OpenAI via `openai` SDK | Best structured output support; abstracted via `BaseAgent` |
| Data validation | Pydantic v2 | Type-safe, fast, serializable; matches JSON agent contracts |
| API framework | FastAPI | Async-native, auto OpenAPI docs, file upload support |
| CLI framework | Typer | Built on Click; type-annotated, auto-generates help |
| DOCX parsing | python-docx | Standard, reliable, no external binaries |
| PDF parsing | pdfplumber | Better table/layout handling than PyPDF |
| DOCX export | python-docx | Full style control for ATS-friendly CV output |
| State management | File-based JSON in `outputs/` | Simple, auditable, no database needed for v1 |
