"""Base model for all LLM-parsed Pydantic models.

Provides universal type coercion and tolerance for LLM JSON output
inconsistencies — extra fields ignored, numbers coerced to strings,
None coerced to empty lists, etc.
"""

from __future__ import annotations

import typing
from typing import Any, get_type_hints

from pydantic import BaseModel, ConfigDict, model_validator


def _is_list_type(annotation: Any) -> bool:
    """Check if a type annotation is ``list[...]`` or ``List[...]``."""
    origin = getattr(annotation, "__origin__", None)
    if origin is list:
        return True
    # typing.List case
    if origin is not None and issubclass(origin, list):
        return True
    # Raw `list` (no generic args)
    if annotation is list:
        return True
    return False


class LLMSafeModel(BaseModel):
    """Base class for all models that parse LLM-generated JSON.

    Features:
    - ``extra="ignore"`` — unknown fields from LLM are silently dropped
    - ``coerce_numbers_to_str=True`` — int/float auto-converted to str
    - Pre-validation: None → [] for any field typed as ``list``
    """

    model_config = ConfigDict(extra="ignore", coerce_numbers_to_str=True)

    @model_validator(mode="before")
    @classmethod
    def _coerce_nulls_to_defaults(cls, values: Any) -> Any:
        """Walk all fields and coerce None values to safe defaults.

        - ``list[...]`` fields: None → []
        """
        if not isinstance(values, dict):
            return values

        # Resolve actual type hints (resolves stringified annotations)
        try:
            hints = get_type_hints(cls)
        except Exception:
            hints = {}

        for field_name in cls.model_fields:
            if field_name not in values:
                continue
            if values[field_name] is not None:
                continue

            # Check resolved type hint
            annotation = hints.get(field_name)
            if annotation and _is_list_type(annotation):
                values[field_name] = []

        return values
