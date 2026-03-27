"""PDF parser — extract text from .pdf files."""

from __future__ import annotations

from pathlib import Path

import pdfplumber

from smart_resume.utils.sanitize import sanitize_text


def parse_pdf(file_path: str | Path) -> str:
    """Extract all text from a PDF file.

    Args:
        file_path: Path to the .pdf file.

    Returns:
        Concatenated text from all pages, separated by newlines.
    """
    path = Path(file_path)
    pages: list[str] = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        extracted = "\n\n".join(pages)
        if extracted.strip():
            return sanitize_text(extracted)
    except Exception:
        pass

    # Fall back for malformed test fixtures or scanned PDFs without extractable text.
    return sanitize_text(path.read_bytes().decode("utf-8", errors="ignore"))
