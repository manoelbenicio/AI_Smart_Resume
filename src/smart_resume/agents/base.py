"""Base agent abstraction — all 7 agents inherit from this."""

from __future__ import annotations

import json
import random
import re
import time
from abc import ABC, abstractmethod
from typing import Any

from openai import OpenAI
import structlog

from smart_resume.config import settings

logger = structlog.get_logger(__name__)


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
        max_retries = 3
        timeout_seconds = 120
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        for attempt in range(1, max_retries + 1):
            logger.info(
                "llm_call_start",
                agent=self.agent_name,
                model=self._model,
                attempt=attempt,
                max_retries=max_retries,
            )
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    timeout=timeout_seconds,
                )
                content = response.choices[0].message.content or ""
                logger.debug(
                    "llm_call_success",
                    agent=self.agent_name,
                    model=self._model,
                    response_chars=len(content),
                )
                return content
            except Exception:
                if attempt >= max_retries:
                    logger.exception(
                        "llm_call_failed_final",
                        agent=self.agent_name,
                        model=self._model,
                        attempt=attempt,
                        max_retries=max_retries,
                    )
                    raise

                backoff = (2 ** (attempt - 1)) + random.uniform(0, 1)
                logger.warning(
                    "llm_call_failed_retrying",
                    agent=self.agent_name,
                    model=self._model,
                    attempt=attempt,
                    max_retries=max_retries,
                    backoff_seconds=round(backoff, 2),
                    exc_info=True,
                )
                time.sleep(backoff)

        raise RuntimeError(f"[{self.agent_name}] Unreachable retry state in _call_llm")

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
