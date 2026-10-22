"""Server error details survive streamed requests (issue #52).

The mock server streams bodies from a generator, like a real network
response: nothing is buffered until read, and once the ``client.stream(...)``
block exits the body is gone (``httpx.StreamClosed``). With plain
``response.raise_for_status()`` that dropped the server's
``Invalid agent 'SplunkAgent'`` and users saw a bare ``400 Bad Request``.
"""

import io
import json
from unittest.mock import Mock, patch

import httpx
import pandas as pd
import pytest

from louieai._client import LouieClient
from louieai._http import error_detail, raise_for_status

_RealClient = httpx.Client
INVALID_AGENT = {"detail": "Invalid agent 'SplunkAgent'"}
URL = "https://louie.test/api/chat/"


class _GeneratorStream(httpx.SyncByteStream):
    """Unbuffered body, as received from a real server."""

    def __init__(self, body: bytes):
        self._body = body

    def __iter__(self):
        yield self._body


def _reply(status: int, body: bytes | str | dict) -> httpx.Response:
    if isinstance(body, dict):
        body = json.dumps(body)
    if isinstance(body, str):
        body = body.encode()
    return httpx.Response(status, stream=_GeneratorStream(body))


def _transport(status: int, body: bytes | str | dict = b"") -> httpx.MockTransport:
    return httpx.MockTransport(lambda request: _reply(status, body))


def _client_factory(transport: httpx.MockTransport):
    """Stand-in for ``httpx.Client(...)`` that routes to ``transport``."""

    def make(*args, **kwargs):
        kwargs.pop("transport", None)
        return _RealClient(*args, transport=transport, **kwargs)

    return make


def _streamed_error(
    status: int, body: bytes | str | dict = b""
) -> httpx.HTTPStatusError:
    with (
        _RealClient(transport=_transport(status, body)) as client,
        client.stream("POST", URL) as response,
        pytest.raises(httpx.HTTPStatusError) as excinfo,
    ):
        raise_for_status(response)
    return excinfo.value


class TestRaiseForStatus:
    def test_baseline_plain_raise_for_status_loses_body(self):
        """The bug: httpx's message omits the body, and it can't be read later."""
        with _RealClient(transport=_transport(400, INVALID_AGENT)) as client:
            with (
                client.stream("POST", URL) as response,
                pytest.raises(httpx.HTTPStatusError) as excinfo,
            ):
                response.raise_for_status()
            assert "Invalid agent" not in str(excinfo.value)
            with pytest.raises(httpx.StreamClosed):
                excinfo.value.response.read()

    def test_streamed_json_detail_in_message(self):
        message = str(_streamed_error(400, INVALID_AGENT))
        first, second, *_ = message.splitlines()
        assert first.startswith("Client error '400 Bad Request'")
        assert second == "Server detail: Invalid agent 'SplunkAgent'"
        assert "developer.mozilla.org" in message  # httpx's hint line is kept

    def test_body_stays_readable_after_stream_closes(self):
        error = _streamed_error(400, INVALID_AGENT)
        assert error.response.status_code == 400
        assert error.response.json() == INVALID_AGENT

    def test_non_json_body_used_verbatim(self):
        error = _streamed_error(502, "upstream unavailable")
        assert "Server detail: upstream unavailable" in str(error)

    def test_structured_detail_is_serialized_without_request_echo(self):
        detail = [
            {
                "loc": ["header", "x"],
                "msg": "field required",
                "input": "Bearer secret-token",
            }
        ]
        message = str(_streamed_error(422, {"detail": detail}))
        assert '"msg": "field required"' in message
        assert "secret-token" not in message

    @pytest.mark.parametrize("body", [b"", b"   ", b'{"detail": null}'])
    def test_no_detail_keeps_original_error(self, body):
        error = _streamed_error(500, body)
        assert "Server detail" not in str(error)
        assert error.response.status_code == 500

    def test_unreadable_body_keeps_original_error(self):
        class _Broken(httpx.SyncByteStream):
            def __iter__(self):
                raise httpx.ReadError("connection reset")
                yield b""  # pragma: no cover

        transport = httpx.MockTransport(
            lambda request: httpx.Response(400, stream=_Broken())
        )
        with (
            _RealClient(transport=transport) as client,
            client.stream("POST", URL) as response,
            pytest.raises(httpx.HTTPStatusError) as excinfo,
        ):
            raise_for_status(response)
        assert "Server detail" not in str(excinfo.value)

    def test_success_does_not_raise(self):
        with (
            _RealClient(transport=_transport(200, "{}")) as client,
            client.stream("POST", URL) as response,
        ):
            raise_for_status(response)


class TestErrorDetail:
    def test_long_detail_truncated_with_marker(self):
        detail = error_detail(httpx.Response(400, text="x" * 5000))
        assert len(detail) == 500
        assert detail.endswith("…")

    def test_control_characters_and_newlines_flattened(self):
        body = "bad\nServer detail: forged\x1b[31m line"
        assert error_detail(httpx.Response(400, text=body)) == (
            "bad Server detail: forged [31m line"
        )

    def test_deeply_nested_json_falls_back_to_text(self):
        body = "[" * 100_000
        assert error_detail(httpx.Response(400, text=body)).startswith("[[[")


@pytest.fixture
def louie_client():
    graphistry_client = Mock()
    graphistry_client.api_token = Mock(return_value="fake-token")
    return LouieClient(
        server_url="https://louie.test", graphistry_client=graphistry_client
    )


def _patched(status: int, body):
    return patch("httpx.Client", _client_factory(_transport(status, body)))


class TestCallSitesSurfaceDetail:
    """Each entry point that takes ``agent=`` reports the server's reason."""

    def test_add_cell(self, louie_client):
        with (
            _patched(400, INVALID_AGENT),
            pytest.raises(httpx.HTTPStatusError, match="Invalid agent 'SplunkAgent'"),
        ):
            louie_client.add_cell("", "hi", agent="SplunkAgent")

    def test_chat_singleshot(self, louie_client):
        louie_client._client = _RealClient(transport=_transport(400, INVALID_AGENT))
        with pytest.raises(httpx.HTTPStatusError, match="Invalid agent 'SplunkAgent'"):
            louie_client.add_cell("", "hi", agent="SplunkAgent", use_batch=True)

    def test_notebook_stream_response(self, louie_client):
        from louieai.notebook.streaming import stream_response

        with (
            _patched(400, INVALID_AGENT),
            pytest.raises(httpx.HTTPStatusError, match="Invalid agent 'SplunkAgent'"),
        ):
            stream_response(louie_client, "", "hi", agent="SplunkAgent")

    def test_upload_dataframe(self, louie_client):
        with (
            _patched(400, {"detail": "Invalid agent 'UploadAgent'"}),
            pytest.raises(httpx.HTTPStatusError, match="Invalid agent 'UploadAgent'"),
        ):
            louie_client.upload_dataframe(
                "hi", pd.DataFrame({"a": [1]}), agent="UploadAgent"
            )

    def test_upload_image(self, louie_client):
        png = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
        with (
            _patched(400, {"detail": "Invalid agent 'UploadAgent'"}),
            pytest.raises(httpx.HTTPStatusError, match="Invalid agent 'UploadAgent'"),
        ):
            louie_client.upload_image("hi", png, agent="UploadAgent")

    def test_upload_binary(self, louie_client):
        pdf = io.BytesIO(b"%PDF-1.4\n%%EOF\n")
        with (
            _patched(400, {"detail": "Invalid agent 'UploadAgent'"}),
            pytest.raises(httpx.HTTPStatusError, match="Invalid agent 'UploadAgent'"),
        ):
            louie_client.upload_binary("hi", pdf, agent="UploadAgent")


def test_streamed_expired_jwt_refreshes_and_retries(louie_client):
    """A readable 401 body lets ``auto_retry_auth`` see the JWT error.

    Before #52 the streamed body was closed, so the expired-token refresh
    never triggered for ``add_cell``.
    """
    replies = [
        _reply(401, {"detail": "JWT token expired"}),
        _reply(200, '{"type": "StreamingApiMessageStart", "dthread_id": "D_1"}\n'),
    ]
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return replies[len(requests) - 1]

    graphistry_client = louie_client._auth_manager._graphistry_client
    with patch("httpx.Client", _client_factory(httpx.MockTransport(handler))):
        response = louie_client.add_cell("", "hi")

    assert len(requests) == 2
    graphistry_client.refresh.assert_called_once()
    assert response.thread_id == "D_1"
