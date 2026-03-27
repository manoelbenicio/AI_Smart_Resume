"""Unit tests for text/payload sanitization utilities."""

from __future__ import annotations

from smart_resume.utils.sanitize import sanitize_payload, sanitize_text


def test_sanitize_text_removes_control_chars_and_keeps_common_whitespace() -> None:
    value = "A\x00B\x01C\tD\nE\rF\x7f"
    assert sanitize_text(value) == "ABC\tD\nE\rF"


def test_sanitize_payload_recursively_cleans_nested_structures() -> None:
    payload = {
        "title": "Head\x00line",
        "items": ["ok", "bad\x1fvalue"],
        "nested": {
            "body": "hello\x0bworld",
            "list": [{"k": "v\x00"}, 7, None],
        },
    }
    sanitized = sanitize_payload(payload)

    assert sanitized["title"] == "Headline"
    assert sanitized["items"] == ["ok", "badvalue"]
    assert sanitized["nested"]["body"] == "helloworld"
    assert sanitized["nested"]["list"][0]["k"] == "v"
    assert sanitized["nested"]["list"][1] == 7
    assert sanitized["nested"]["list"][2] is None

