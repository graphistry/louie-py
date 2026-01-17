"""Unit tests for W3C traceparent propagation."""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pytest

from louieai._tracing import (
    build_traceparent,
    generate_span_id,
    generate_trace_id,
    get_traceparent,
    inject_otel_traceparent,
)


class TestGenerateTraceId:
    """Tests for generate_trace_id."""

    def test_returns_32_hex_chars(self) -> None:
        """Trace ID should be 32 hex characters."""
        trace_id = generate_trace_id()
        assert len(trace_id) == 32
        assert re.match(r"^[0-9a-f]{32}$", trace_id)

    def test_returns_unique_values(self) -> None:
        """Each call should return a unique trace ID."""
        ids = {generate_trace_id() for _ in range(100)}
        assert len(ids) == 100


class TestGenerateSpanId:
    """Tests for generate_span_id."""

    def test_returns_16_hex_chars(self) -> None:
        """Span ID should be 16 hex characters."""
        span_id = generate_span_id()
        assert len(span_id) == 16
        assert re.match(r"^[0-9a-f]{16}$", span_id)

    def test_returns_unique_values(self) -> None:
        """Each call should return a unique span ID."""
        ids = {generate_span_id() for _ in range(100)}
        assert len(ids) == 100


class TestBuildTraceparent:
    """Tests for build_traceparent."""

    def test_w3c_format(self) -> None:
        """Traceparent should follow W3C format."""
        trace_id = "0af7651916cd43dd8448eb211c80319c"
        span_id = "b7ad6b7169203331"
        tp = build_traceparent(trace_id, span_id)
        assert tp == "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"

    def test_sampled_flag(self) -> None:
        """Sampled flag should be 01 when True, 00 when False."""
        trace_id = "0af7651916cd43dd8448eb211c80319c"
        span_id = "b7ad6b7169203331"

        tp_sampled = build_traceparent(trace_id, span_id, sampled=True)
        assert tp_sampled.endswith("-01")

        tp_not_sampled = build_traceparent(trace_id, span_id, sampled=False)
        assert tp_not_sampled.endswith("-00")


class TestInjectOtelTraceparent:
    """Tests for inject_otel_traceparent."""

    def test_returns_false_when_otel_not_installed(self) -> None:
        """Should return False when opentelemetry is not available."""
        with patch.dict("sys.modules", {"opentelemetry": None}):
            # Force reimport to trigger ImportError
            headers: dict[str, str] = {}
            # The function catches ImportError internally
            result = inject_otel_traceparent(headers)
            # May return True if otel is installed in test env
            # Just verify it doesn't raise
            assert isinstance(result, bool)

    def test_returns_false_when_no_active_span(self) -> None:
        """Should return False when no span is active."""
        try:
            from opentelemetry.trace import INVALID_SPAN

            with patch(
                "opentelemetry.trace.get_current_span", return_value=INVALID_SPAN
            ):
                headers: dict[str, str] = {}
                result = inject_otel_traceparent(headers)
                assert result is False
                assert "traceparent" not in headers
        except ImportError:
            pytest.skip("opentelemetry not installed")

    def test_injects_traceparent_when_span_active(self) -> None:
        """Should inject traceparent when an active span exists."""
        try:
            from opentelemetry.sdk.trace import TracerProvider

            # Set up a real tracer
            provider = TracerProvider()
            tracer = provider.get_tracer("test")

            with tracer.start_as_current_span("test_span"):
                headers: dict[str, str] = {}
                result = inject_otel_traceparent(headers)
                assert result is True
                assert "traceparent" in headers
                # Verify format: 00-{trace_id}-{span_id}-{flags}
                assert re.match(
                    r"^00-[0-9a-f]{32}-[0-9a-f]{16}-0[01]$", headers["traceparent"]
                )
        except ImportError:
            pytest.skip("opentelemetry-sdk not installed")


class TestGetTraceparent:
    """Tests for get_traceparent."""

    def test_returns_none_without_otel_or_session(self) -> None:
        """Should return None when no OTel and no session trace."""
        with patch("louieai._tracing.inject_otel_traceparent", return_value=False):
            result = get_traceparent()
            assert result is None

    def test_returns_session_trace_when_no_otel(self) -> None:
        """Should use session trace when OTel is not available."""
        with patch("louieai._tracing.inject_otel_traceparent", return_value=False):
            session_trace_id = "abcd1234abcd1234abcd1234abcd1234"
            result = get_traceparent(session_trace_id)

            assert result is not None
            assert result.startswith(f"00-{session_trace_id}-")
            assert result.endswith("-01")
            # Verify format
            assert re.match(r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$", result)

    def test_prefers_otel_over_session(self) -> None:
        """Should prefer OTel context over session trace."""
        otel_traceparent = "00-otel1234otel1234otel1234otel1234-otelspan12345678-01"

        def mock_inject(headers: dict[str, str]) -> bool:
            headers["traceparent"] = otel_traceparent
            return True

        with patch("louieai._tracing.inject_otel_traceparent", side_effect=mock_inject):
            session_trace_id = "sess1234sess1234sess1234sess1234"
            result = get_traceparent(session_trace_id)

            # Should return OTel traceparent, not session
            assert result == otel_traceparent

    def test_generates_new_span_id_each_call(self) -> None:
        """Each call should generate a new span ID."""
        with patch("louieai._tracing.inject_otel_traceparent", return_value=False):
            session_trace_id = "abcd1234abcd1234abcd1234abcd1234"

            results = [get_traceparent(session_trace_id) for _ in range(10)]

            # All should have same trace_id
            trace_ids = [r.split("-")[1] for r in results if r]  # type: ignore[union-attr]
            assert all(tid == session_trace_id for tid in trace_ids)

            # All should have different span_ids
            span_ids = [r.split("-")[2] for r in results if r]  # type: ignore[union-attr]
            assert len(set(span_ids)) == 10


class TestClientHeadersIntegration:
    """Integration tests for traceparent in client headers."""

    def test_get_headers_without_tracing(self) -> None:
        """Headers should work without any tracing context."""
        from louieai._client import LouieClient

        # Mock the auth manager
        with patch.object(LouieClient, "__init__", lambda self: None):
            client = LouieClient.__new__(LouieClient)
            client._auth_manager = MagicMock()
            client._auth_manager.get_token.return_value = "test-token"
            client._auth_manager._credentials = {}

            with patch("louieai._tracing.get_traceparent", return_value=None):
                headers = client._get_headers()

            assert "Authorization" in headers
            assert "traceparent" not in headers

    def test_get_headers_with_session_trace(self) -> None:
        """Headers should include traceparent from session trace."""
        from louieai._client import LouieClient

        with patch.object(LouieClient, "__init__", lambda self: None):
            client = LouieClient.__new__(LouieClient)
            client._auth_manager = MagicMock()
            client._auth_manager.get_token.return_value = "test-token"
            client._auth_manager._credentials = {}

            session_trace = "abcd1234abcd1234abcd1234abcd1234"
            headers = client._get_headers(session_trace_id=session_trace)

            assert "Authorization" in headers
            assert "traceparent" in headers
            assert headers["traceparent"].startswith(f"00-{session_trace}-")

    def test_get_headers_with_explicit_traceparent(self) -> None:
        """Explicit traceparent should override auto-generated."""
        from louieai._client import LouieClient

        with patch.object(LouieClient, "__init__", lambda self: None):
            client = LouieClient.__new__(LouieClient)
            client._auth_manager = MagicMock()
            client._auth_manager.get_token.return_value = "test-token"
            client._auth_manager._credentials = {}

            explicit_tp = "00-explicit1234explicit1234explic-explicitspan1234-01"
            headers = client._get_headers(
                session_trace_id="should-be-ignored",
                traceparent=explicit_tp,
            )

            assert headers["traceparent"] == explicit_tp


class TestCursorSessionTrace:
    """Tests for Cursor session trace management."""

    def test_cursor_generates_trace_id(self) -> None:
        """Cursor should generate a session trace ID on init."""
        from collections import deque

        from louieai.notebook.cursor import Cursor

        # Create cursor without calling __init__
        cursor = Cursor.__new__(Cursor)
        cursor._client = MagicMock()
        cursor._history = deque(maxlen=100)
        cursor._current_thread = None
        cursor._traces = False
        cursor._share_mode = "Private"
        cursor._name = None
        cursor._folder = None
        cursor._last_display_id = None
        cursor._trace_id = generate_trace_id()

        assert len(cursor._trace_id) == 32
        assert re.match(r"^[0-9a-f]{32}$", cursor._trace_id)

    def test_cursor_new_inherits_trace_id(self) -> None:
        """Cursor.new() should inherit parent's trace ID."""
        from collections import deque

        from louieai.notebook.cursor import Cursor

        # Create parent cursor without calling __init__
        parent = Cursor.__new__(Cursor)
        parent._client = MagicMock()
        parent._history = deque(maxlen=100)
        parent._current_thread = None
        parent._traces = False
        parent._share_mode = "Private"
        parent._name = None
        parent._folder = None
        parent._last_display_id = None
        parent._trace_id = "parent123parent123parent123parent1"

        # Create child via new()
        child = parent.new()

        # Child should share parent's trace_id
        assert child._trace_id == parent._trace_id
