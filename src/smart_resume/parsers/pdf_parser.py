"""PDF parser — extract text from .pdf files."""

from __future__ import annotations

from pathlib import Path

import pdfplumber


def parse_pdf(file_path: str | Path) -> str:
    """Extract all text from a PDF file.

    Args:
        file_path: Path to the .pdf file.

    Returns:
        Concatenated text from all pages, separated by newlines.
    """
    pages: list[str] = []
    with pdfplumber.open(str(file_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n\n".join(pages)
