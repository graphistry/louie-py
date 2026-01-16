"""W3C Traceparent propagation for distributed tracing.

This module provides traceparent header generation for correlating
louie-py requests with distributed traces. It supports:

1. OpenTelemetry integration: If OTel is configured with an active span,
   the current trace context is automatically propagated.

2. Session-level correlation: When OTel is not available, a session
   trace_id is used to correlate all requests from a Cursor instance.

The traceparent header follows the W3C Trace Context specification:
https://www.w3.org/TR/trace-context/
"""

from __future__ import annotations

import secrets


def generate_trace_id() -> str:
    """Generate a random 32-character hex trace ID."""
    return secrets.token_hex(16)


def generate_span_id() -> str:
    """Generate a random 16-character hex span ID."""
    return secrets.token_hex(8)


def build_traceparent(trace_id: str, span_id: str, sampled: bool = True) -> str:
    """Build a W3C traceparent header value.

    Format: {version}-{trace_id}-{span_id}-{trace_flags}
    Example: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01

    Args:
        trace_id: 32-character hex trace ID
        span_id: 16-character hex span ID
        sampled: Whether the trace is sampled (default True)

    Returns:
        W3C traceparent header value
    """
    flags = "01" if sampled else "00"
    return f"00-{trace_id}-{span_id}-{flags}"


def inject_otel_traceparent(headers: dict[str, str]) -> bool:
    """Inject traceparent from OpenTelemetry context if available.

    Uses the standard OTel propagate.inject() mechanism which handles
    W3C Trace Context, baggage, and any configured propagators.

    Args:
        headers: Dict to inject traceparent into (modified in place)

    Returns:
        True if OTel context was injected, False otherwise
    """
    try:
        from opentelemetry.propagate import inject
        from opentelemetry.trace import INVALID_SPAN, get_current_span

        span = get_current_span()
        if span == INVALID_SPAN or not span.is_recording():
            return False

        inject(headers)
        return True
    except ImportError:
        return False


def get_traceparent(session_trace_id: str | None = None) -> str | None:
    """Get traceparent header value for an outgoing request.

    Priority:
    1. Active OTel span context (if available)
    2. Session trace_id with new span_id (if provided)
    3. None (no tracing)

    Args:
        session_trace_id: Optional session-level trace ID for correlation
            when OTel is not available

    Returns:
        traceparent header value or None
    """
    # Try OTel first
    headers: dict[str, str] = {}
    if inject_otel_traceparent(headers):
        return headers.get("traceparent")

    # Fallback to session trace
    if session_trace_id:
        span_id = generate_span_id()
        return build_traceparent(session_trace_id, span_id)

    return None
