"""FastAPI application — Executive CV Benchmark Engine REST API."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from smart_resume.api.auth_routes import router as auth_router
from smart_resume.api.routes import router
from smart_resume.db.base import Base
from smart_resume.db.engine import engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-28s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)

app = FastAPI(
    title="Executive CV Benchmark Engine",
    description=(
        "Multi-agent system that evaluates executive CVs against job descriptions, "
        "scores market positioning, benchmarks against archetypes, identifies risks, "
        "and generates repositioned CVs."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)


@app.on_event("startup")
async def init_database() -> None:
    """Create DB tables if they do not exist yet."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "smart-ai-resume"}
