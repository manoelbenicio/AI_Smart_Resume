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
        # Strip markdown fences
        cleaned = re.sub(r"```(?:json)?\s*", "", raw)
        cleaned = cleaned.strip().rstrip("`")

        # Find first { or [
        start = -1
        for i, ch in enumerate(cleaned):
            if ch in ("{", "["):
                start = i
                break
        if start == -1:
            raise ValueError(f"[{self.agent_name}] No JSON found in LLM response")

        # Find matching closing brace/bracket
        open_char = cleaned[start]
        close_char = "}" if open_char == "{" else "]"
        depth = 0
        end = start
        for i in range(start, len(cleaned)):
            if cleaned[i] == open_char:
                depth += 1
            elif cleaned[i] == close_char:
                depth -= 1
                if depth == 0:
                    end = i
                    break

        json_str = cleaned[start : end + 1]
        try:
            return json.loads(json_str)  # type: ignore[no-any-return]
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"[{self.agent_name}] Failed to parse JSON: {exc}\nExtracted: {json_str[:500]}"
            ) from exc

    # ─── Abstract interface ──────────────────────────────────────

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Execute the agent's task. Subclasses define inputs/outputs."""
        ...
