"""HTTP helpers shared by the client, upload, and notebook streaming paths."""

from __future__ import annotations

import contextlib
import json

import httpx

_MAX_DETAIL_CHARS = 500


def error_detail(response: httpx.Response) -> str:
    """Return the server's error explanation from a read response, or ``""``.

    Louie's API errors are JSON ``{"detail": ...}``; anything else falls back to
    the (truncated) body text.
    """
    try:
        text = response.text
    except httpx.ResponseNotRead:
        return ""
    if not isinstance(text, str) or not text.strip():
        return ""
    text = text.strip()
    try:
        data = json.loads(text)
    except ValueError:
        return text[:_MAX_DETAIL_CHARS]
    if isinstance(data, dict) and "detail" in data:
        detail = data["detail"]
        text = detail if isinstance(detail, str) else json.dumps(detail)
    return text[:_MAX_DETAIL_CHARS]


def raise_for_status(response: httpx.Response) -> None:
    """``response.raise_for_status()`` that keeps the server's error detail.

    A streamed response is closed by the time the caller's ``except`` runs, so
    its body (e.g. ``{"detail": "Invalid agent 'X'"}``) is otherwise lost and
    users see only ``400 Bad Request``. Read it first, and put the detail in the
    message; ``e.response.text`` / ``.json()`` also stay readable.
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
