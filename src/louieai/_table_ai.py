"""Shared helpers for Table AI override handling."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

JSONLike = dict[str, Any] | list[Any] | str | int | float | bool

_TABLE_AI_KEY_TRANSLATIONS: dict[str, str] = {
    "semantic_mode": "table_ai_semantic_mode",
    "output_column": "table_ai_output_column",
    "ask_model": "table_ai_ask_model",
    "evidence_model": "table_ai_evidence_model",
    "options": "table_ai_options",
    "ask_options": "table_ai_ask_options",
    "evidence_options": "table_ai_evidence_options",
}
_TABLE_AI_PARAM_KEYS = frozenset(_TABLE_AI_KEY_TRANSLATIONS.values())


def _jsonify(value: JSONLike) -> JSONLike | str:
    if isinstance(value, str):
        return value
    return json.dumps(value)


@dataclass(slots=True)
class TableAIOverrides:
    """Structured holder for Louie Table AI override parameters."""

    semantic_mode: str | None = None
    output_column: str | None = None
    ask_model: str | None = None
    evidence_model: str | None = None
    options: JSONLike | None = None
    ask_options: JSONLike | None = None
    evidence_options: JSONLike | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> TableAIOverrides:
        """Create overrides from an arbitrary mapping."""

        return cls(
            semantic_mode=data.get("semantic_mode")
            or data.get("table_ai_semantic_mode"),
            output_column=data.get("output_column")
            or data.get("table_ai_output_column"),
            ask_model=data.get("ask_model") or data.get("table_ai_ask_model"),
            evidence_model=data.get("evidence_model")
            or data.get("table_ai_evidence_model"),
            options=data.get("options") or data.get("table_ai_options"),
            ask_options=data.get("ask_options") or data.get("table_ai_ask_options"),
            evidence_options=data.get("evidence_options")
            or data.get("table_ai_evidence_options"),
        )

    def to_params(self) -> dict[str, Any]:
        """Convert overrides into API parameter names."""

        params: dict[str, Any] = {}
        if self.semantic_mode is not None:
            params["table_ai_semantic_mode"] = self.semantic_mode
        if self.output_column is not None:
            params["table_ai_output_column"] = self.output_column
        if self.ask_model is not None:
            params["table_ai_ask_model"] = self.ask_model
        if self.evidence_model is not None:
            params["table_ai_evidence_model"] = self.evidence_model
        if self.options is not None:
            params["table_ai_options"] = _jsonify(self.options)
        if self.ask_options is not None:
            params["table_ai_ask_options"] = _jsonify(self.ask_options)
        if self.evidence_options is not None:
            params["table_ai_evidence_options"] = _jsonify(self.evidence_options)
        return params


def normalize_table_ai_overrides(
    overrides: TableAIOverrides | Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Normalize overrides into API parameter dict."""

    if overrides is None:
        return {}
    if isinstance(overrides, TableAIOverrides):
        model = overrides
    elif isinstance(overrides, Mapping):
        model = TableAIOverrides.from_mapping(overrides)
    else:
        raise TypeError(
            "table_ai_overrides must be TableAIOverrides or mapping, "
            f"got {type(overrides).__name__}"
        )
    return model.to_params()


def collect_table_ai_kwargs(source: dict[str, Any]) -> dict[str, Any]:
    """Extract legacy Table AI kwargs into API parameters.

    Mutates ``source`` by removing recognized keys. Raises TypeError if mixed keys are
    incompatible (handled by caller once unrecognized keys remain).
    """

    if not source:
        return {}

    extracted: dict[str, Any] = {}

    for key in list(source.keys()):
        if key in _TABLE_AI_PARAM_KEYS:
            extracted[key] = source.pop(key)

    for short_key, param_key in _TABLE_AI_KEY_TRANSLATIONS.items():
        if short_key in source:
            extracted[param_key] = source.pop(short_key)

    if not extracted:
        return {}

    return TableAIOverrides.from_mapping(extracted).to_params()


__all__ = [
    "JSONLike",
    "TableAIOverrides",
    "collect_table_ai_kwargs",
    "normalize_table_ai_overrides",
]
