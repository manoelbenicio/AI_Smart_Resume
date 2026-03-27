"""Base agent abstraction — all 7 agents inherit from this."""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any

from openai import OpenAI

from smart_resume.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base for all pipeline agents.

    Provides:
    - LLM client initialisation
    - Prompt execution with structured JSON extraction
    - Standard error handling
    """

    agent_name: str = "BaseAgent"

    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.llm_model
        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens

    # ─── LLM helpers ─────────────────────────────────────────────

    def _call_llm(self, user_prompt: str, system_prompt: str = "") -> str:
        """Send a prompt to the LLM and return raw text response."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        logger.info("[%s] Calling LLM (%s) …", self.agent_name, self._model)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        content = response.choices[0].message.content or ""
        logger.debug("[%s] Raw response length: %d chars", self.agent_name, len(content))
        return content

    def _parse_json(self, raw: str) -> dict[str, Any]:
        """Extract and parse the first JSON object or array from LLM output.

        Handles responses wrapped in ```json ... ``` fences.
        """
        cleaned = re.sub(r"```(?:json)?\s*", "", raw)
        cleaned = cleaned.strip().rstrip("`")

        decoder = json.JSONDecoder()
        for i, ch in enumerate(cleaned):
            if ch not in ("{", "["):
                continue
            snippet = cleaned[i:]
            try:
                parsed, _ = decoder.raw_decode(snippet)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list):
                return {"items": parsed}

        preview = cleaned[:500]
        raise ValueError(f"[{self.agent_name}] Failed to parse JSON from response. Preview: {preview}")

    # ─── Abstract interface ──────────────────────────────────────

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Execute the agent's task. Subclasses define inputs/outputs."""
        ...
