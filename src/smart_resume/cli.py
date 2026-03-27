"""CLI entry point — Typer-based command-line interface."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from smart_resume.orchestrator import Orchestrator

app = typer.Typer(
    name="smart-resume",
    help="Executive CV Benchmark Engine — Analyse and reposition CVs for maximum market impact.",
    no_args_is_help=True,
)
console = Console()

CATEGORY_LABELS = {
    "scale": "Scale",
    "strategic_complexity": "Strategic Complexity",
    "transformation_history": "Transformation History",
    "competitive_differentiation": "Competitive Differentiation",
    "international_experience": "International Experience",
    "career_progression_speed": "Career Progression Speed",
    "financial_impact": "Financial Impact",
    "executive_presence": "Executive Presence",
}


@app.command()
def analyze(
    cv: str = typer.Option(..., "--cv", help="Path to CV file (docx/pdf/txt) or raw text"),
    jd: str = typer.Option(..., "--jd", help="Job description text, file path, or URL"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
) -> None:
    """Run the full 8-phase benchmark pipeline on a CV against a job description."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s │ %(name)-28s │ %(levelname)-7s │ %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    console.print(Panel(">> [bold cyan]Executive CV Benchmark Engine[/bold cyan]", expand=False))

    orchestrator = Orchestrator()
    state = orchestrator.run(cv_input=cv, jd_input=jd)

    # ─── Display Results ───
    console.print()
    console.print(Panel(f"[bold green]Pipeline Complete[/bold green] — Run ID: {state.run_id}"))

    # Category Scores
    if state.scoring:
        table = Table(title="Market Positioning Scores")
        table.add_column("Category", style="cyan")
        table.add_column("Score", justify="right", style="bold")
        table.add_column("Explanation")

        scores = state.scoring.category_scores.model_dump()
        for field_name, label in CATEGORY_LABELS.items():
            score = float(scores.get(field_name, 0))
            explanation = state.scoring.explanations.get(field_name, "")
            table.add_row(label, f"{score:.0f}", explanation[:80])

        table.add_section()
        table.add_row("[bold]OVERALL[/bold]", f"[bold]{state.scoring.overall_score:.1f}[/bold]", "")
        console.print(table)

    # Final Score
    console.print(f"\n[bold]Final Re-Evaluation Score:[/bold] {state.final_score:.1f}/100")
    console.print(f"[bold]Iterations Used:[/bold] {state.iterations_used}")

    # Output paths
    if state.output_docx_path:
        console.print(f"[bold]DOCX:[/bold] {state.output_docx_path}")
    if state.output_pdf_path:
        console.print(f"[bold]PDF:[/bold] {state.output_pdf_path}")

    if state.output_docx_path:
        console.print(f"[bold]Audit Trail:[/bold] {Path(state.output_docx_path).parent / 'pipeline_run.json'}")


if __name__ == "__main__":
    app()
