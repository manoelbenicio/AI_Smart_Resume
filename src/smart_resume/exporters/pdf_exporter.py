"""PDF Exporter — Convert Markdown CV to PDF (optional dependency)."""

from __future__ import annotations

import logging
from pathlib import Path

import markdown as md

logger = logging.getLogger(__name__)


def export_pdf(markdown_cv: str, output_path: str | Path) -> Path | None:
    """Convert a Markdown-formatted CV into a PDF file.

    Requires the optional `weasyprint` dependency.
    Falls back gracefully if weasyprint is not installed.

    Args:
        markdown_cv: The CV content in Markdown.
        output_path: Where to save the PDF.

    Returns:
        Path to the generated PDF, or None if weasyprint is unavailable.
    """
    try:
        from weasyprint import HTML  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("weasyprint not installed — PDF export skipped.  Install with: pip install weasyprint")
        return None

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Split at --- separator (CV vs justification)
    parts = markdown_cv.split("\n---\n", maxsplit=1)
    cv_content = parts[0]

    html_body = md.markdown(cv_content, extensions=["extra", "sane_lists"])

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: 'Calibri', 'Segoe UI', sans-serif; font-size: 11pt;
           color: #2d2d2d; max-width: 800px; margin: 0 auto; padding: 40px; }}
    h1 {{ text-align: center; color: #1a1a2e; border-bottom: 2px solid #16213e; padding-bottom: 8px; }}
    h2 {{ color: #16213e; border-bottom: 1px solid #e0e0e0; padding-bottom: 4px; }}
    h3 {{ color: #0f3460; }}
    ul {{ padding-left: 20px; }}
    li {{ margin-bottom: 4px; }}
    strong {{ color: #e94560; }}
</style>
</head>
<body>{html_body}</body>
</html>"""

    HTML(string=full_html).write_pdf(str(output_path))
    logger.info("PDF exported to %s", output_path)
    return output_path
