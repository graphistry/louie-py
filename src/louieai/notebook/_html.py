"""Small HTML-safety helpers for notebook renderers."""

from __future__ import annotations

import re
from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit

_DATA_IMAGE = re.compile(
    r"^data:image/(?:png|jpeg|gif|webp);base64,[A-Za-z0-9+/\s]*={0,2}$",
    re.IGNORECASE,
)


def safe_http_url(value: object) -> str | None:
    """Return a normalized HTTP(S) URL, or None for unsafe/invalid input."""
    raw = str(value).strip() if value is not None else ""
    if not raw:
        return None
    try:
        parsed = urlsplit(raw)
    except ValueError:
        return None
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None
    return urlunsplit(parsed)


def graph_url(server_url: object, dataset_id: object) -> str | None:
    """Build a safe graph URL with an encoded dataset query value."""
    base = safe_http_url(server_url)
    if base is None or dataset_id is None:
        return None
    parsed = urlsplit(base)
    path = f"{parsed.path.rstrip('/')}/graph/graph.html"
    query = urlencode({"dataset": str(dataset_id)})
    return urlunsplit((parsed.scheme, parsed.netloc, path, query, ""))


def resolve_http_url(value: object, base_url: object) -> str | None:
    """Resolve a relative URL against a safe base and require HTTP(S)."""
    raw = str(value).strip() if value is not None else ""
    if not raw:
        return None
    if raw.startswith("/"):
        base = safe_http_url(base_url)
        if base is None:
            return None
        return safe_http_url(urljoin(f"{base.rstrip('/')}/", raw))
    return safe_http_url(raw)


def safe_image_src(value: object) -> str | None:
    """Allow HTTP(S) images or raster-only base64 data images."""
    raw = str(value).strip() if value is not None else ""
    return safe_http_url(raw) or (raw if _DATA_IMAGE.fullmatch(raw) else None)


def css_pixel_dimension(value: object) -> int | None:
    """Return a bounded positive integer suitable for a CSS pixel value."""
    if isinstance(value, bool) or not isinstance(value, str | int | float):
        return None
    try:
        dimension = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return dimension if 0 < dimension <= 10_000 else None
