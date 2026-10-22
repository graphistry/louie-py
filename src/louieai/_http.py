"""HTTP helpers shared by the client, upload, and notebook streaming paths."""

from __future__ import annotations

import contextlib
import json
import re
from typing import Any

import httpx

_MAX_DETAIL_CHARS = 500
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]+")


def _without_request_echo(detail: Any) -> Any:
    """Drop FastAPI 422 ``input`` fields, which echo back request values."""
    if isinstance(detail, list):
        return [_without_request_echo(item) for item in detail]
    if isinstance(detail, dict):
        return {k: _without_request_echo(v) for k, v in detail.items() if k != "input"}
    return detail


def error_detail(response: httpx.Response) -> str:
    """Return the server's error explanation from a read response, or ``""``.

    Louie's API errors are JSON ``{"detail": ...}``; anything else falls back to
    the body text. The result is a single line without control characters,
    truncated to ``_MAX_DETAIL_CHARS``.
    """
    try:
        text = response.text
    except httpx.ResponseNotRead:
        return ""
    if not isinstance(text, str) or not text.strip():
        return ""
    try:
        data = json.loads(text)
    except (ValueError, RecursionError):
        data = None
    if isinstance(data, dict) and "detail" in data:
        detail = _without_request_echo(data["detail"])
        if detail is None:
            return ""
        text = detail if isinstance(detail, str) else json.dumps(detail)
    text = " ".join(_CONTROL_CHARS.sub(" ", text).split())
    if len(text) > _MAX_DETAIL_CHARS:
        text = text[: _MAX_DETAIL_CHARS - 1] + "…"
    return text


def raise_for_status(response: httpx.Response) -> None:
    """``response.raise_for_status()`` that keeps the server's error detail.

    A streamed response is closed by the time the caller's ``except`` runs, so
    its body (e.g. ``{"detail": "Invalid agent 'X'"}``) is otherwise lost and
    users see only ``400 Bad Request``. Read it first, and put the detail in the
    message. ``e.response.text`` / ``.json()`` also stay readable, which the 401
    token-refresh check in ``auth.py`` relies on.
    """
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        with contextlib.suppress(httpx.HTTPError, httpx.StreamError):
            e.response.read()
        detail = error_detail(e.response)
        if not detail:
            raise
        first, _, rest = str(e).partition("\n")
        message = f"{first}\nServer detail: {detail}"
        if rest:
            message += f"\n{rest}"
        raise httpx.HTTPStatusError(
            message, request=e.request, response=e.response
        ) from None
