"""Text/payload sanitization helpers."""

from __future__ import annotations

import re
from typing import Any

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def sanitize_text(text: str) -> str:
    """Remove NUL/control characters from text while preserving common whitespace."""
    return _CONTROL_CHARS_RE.sub("", text)


def sanitize_payload(value: Any) -> Any:
    """Recursively sanitize JSON-compatible payloads."""
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_payload(item) for key, item in value.items()}
    return value

