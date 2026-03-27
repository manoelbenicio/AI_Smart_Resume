"""DOCX parser — extract text from .docx files."""

from __future__ import annotations

from pathlib import Path

from docx import Document


def parse_docx(file_path: str | Path) -> str:
    """Extract all text from a DOCX file.

    Args:
        file_path: Path to the .docx file.

    Returns:
        Concatenated text from all paragraphs, separated by newlines.
    """
    doc = Document(str(file_path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
