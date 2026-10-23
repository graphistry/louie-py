"""Server error details survive streamed requests (issue #52).

The mock server streams bodies from a generator, like a real network
response: nothing is buffered until read, and once the ``client.stream(...)``
block exits the body is gone (``httpx.StreamClosed``). With plain
``response.raise_for_status()`` that dropped the server's
``Invalid agent 'SplunkAgent'`` and users saw a bare ``400 Bad Request``.

It also covers the expired-JWT refresh-and-retry path for streamed and upload
calls (issue #56): the retry resends the original bytes, and non-JWT 401s and
``token=`` auth are not retried.
"""

import io
import json
import re
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

    @pytest.mark.parametrize("depth", [1_000, 5_000])
    def test_deeply_nested_detail_never_raises(self, depth):
        body = '{"detail": ' + "[" * depth + "]" * depth + "}"
        # Shallow enough: serialized detail; too deep to walk: raw text. No raise.
        assert error_detail(httpx.Response(400, text=body))

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


def _upload_dataframe(client):
    return client.upload_dataframe("hi", pd.DataFrame({"a": [1]}))


def _upload_image(client):
    return client.upload_image("hi", io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16))


def _upload_binary(client):
    return client.upload_binary("hi", io.BytesIO(b"%PDF-1.4\n%%EOF\n"))


@pytest.mark.parametrize(
    ("call", "payload_marker"),
    [
        (lambda client: client.add_cell("", "hi"), None),
        (_upload_dataframe, b"PAR1"),
        (_upload_image, b"\x89PNG"),
        (_upload_binary, b"%PDF-1.4"),
    ],
    ids=["add_cell", "upload_dataframe", "upload_image", "upload_binary"],
)
def test_streamed_expired_jwt_refreshes_and_retries(louie_client, call, payload_marker):
    """A readable 401 body lets ``auto_retry_auth`` see the JWT error.

    Before #52 the streamed body was closed, so the expired-token refresh
    never triggered; uploads also lacked the ``auth_manager`` it looks up.
    """
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return _reply(401, {"detail": "JWT token expired"})
        return _reply(
            200, '{"type": "StreamingApiMessageStart", "dthread_id": "D_1"}\n'
        )

    graphistry_client = louie_client._auth_manager._graphistry_client
    tokens = iter(["old-token", "new-token"])
    current = {"token": next(tokens)}
    graphistry_client.api_token = Mock(side_effect=lambda: current["token"])
    graphistry_client.refresh = Mock(
        side_effect=lambda: current.update(token=next(tokens))
    )
    with patch("httpx.Client", _client_factory(httpx.MockTransport(handler))):
        response = call(louie_client)

    assert len(requests) == 2
    if payload_marker:  # resent intact (multipart boundaries differ)
        assert all(payload_marker in r.content for r in requests)
    graphistry_client.refresh.assert_called_once()
    assert requests[0].headers["authorization"] == "Bearer old-token"
    assert requests[1].headers["authorization"] == "Bearer new-token"
    assert response.thread_id == "D_1"


@pytest.mark.parametrize(
    "call",
    [
        lambda client: client.add_cell("", "hi"),
        _upload_dataframe,
        _upload_image,
        _upload_binary,
    ],
    ids=["add_cell", "upload_dataframe", "upload_image", "upload_binary"],
)
def test_persistent_expired_jwt_retries_exactly_once(louie_client, call):
    """A 401 that survives the refresh is raised after one retry.

    Two requests and one refresh: guards against ``@auto_retry_auth`` being
    stacked on both a public upload method and ``_send_file``.
    """
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return _reply(401, {"detail": "JWT token expired"})

    graphistry_client = louie_client._auth_manager._graphistry_client
    graphistry_client.api_token = Mock(return_value="tok")
    graphistry_client.refresh = Mock()
    with (
        patch("httpx.Client", _client_factory(httpx.MockTransport(handler))),
        pytest.raises(httpx.HTTPStatusError),
    ):
        call(louie_client)

    assert len(requests) == 2
    graphistry_client.refresh.assert_called_once()


class _NoSeekReader:
    """File-like with ``read()`` but no ``seek``: it can be read only once."""

    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        data, self._data = self._data, b""
        return data


def _mid_stream(data: bytes) -> io.BytesIO:
    stream = io.BytesIO(b"SKIPPED-PREFIX" + data)
    stream.seek(len(b"SKIPPED-PREFIX"))
    return stream


@pytest.mark.parametrize(
    "make_input",
    [_NoSeekReader, _mid_stream],
    ids=["no-seek reader", "stream not at position 0"],
)
@pytest.mark.parametrize("method", ["upload_binary", "upload_image"])
def test_upload_retry_resends_identical_payload(louie_client, method, make_input):
    """The retry must resend the bytes sent the first time, not re-read input."""
    payload = (
        b"%PDF-1.4\n%%EOF\n"
        if method == "upload_binary"
        else b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
    )
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return _reply(401, {"detail": "JWT token expired"})
        return _reply(
            200, '{"type": "StreamingApiMessageStart", "dthread_id": "D_1"}\n'
        )

    with patch("httpx.Client", _client_factory(httpx.MockTransport(handler))):
        getattr(louie_client, method)("hi", make_input(payload))

    assert len(requests) == 2
    # The multipart part the server routes on: name and type, not just bytes (#59)
    expected_part = (
        b'filename="file.bin"\r\nContent-Type: application/octet-stream'
        if method == "upload_binary"
        else b'filename="image.png"\r\nContent-Type: image/png'
    )
    for request in requests:
        assert payload in request.content
        assert b"SKIPPED-PREFIX" not in request.content
        assert expected_part in request.content


@pytest.mark.parametrize(
    "call",
    [lambda c: c.add_cell("", "hi"), _upload_dataframe, _upload_image, _upload_binary],
    ids=["add_cell", "upload_dataframe", "upload_image", "upload_binary"],
)
def test_non_jwt_401_is_not_retried(louie_client, call):
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return _reply(401, {"detail": "Could not validate credentials"})

    graphistry_client = louie_client._auth_manager._graphistry_client
    with (
        patch("httpx.Client", _client_factory(httpx.MockTransport(handler))),
        pytest.raises(httpx.HTTPStatusError, match="Could not validate credentials"),
    ):
        call(louie_client)
    assert len(requests) == 1
    graphistry_client.refresh.assert_not_called()


@pytest.mark.parametrize(
    "call",
    [lambda c: c.add_cell("", "hi"), _upload_dataframe, _upload_image, _upload_binary],
    ids=["add_cell", "upload_dataframe", "upload_image", "upload_binary"],
)
def test_token_auth_cannot_refresh_so_401_propagates(call):
    """With ``token=`` there is nothing to refresh: one request, original 401."""
    client = LouieClient(server_url="https://louie.test", token="fixed-token")
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return _reply(401, {"detail": "JWT token expired"})

    with (
        patch("httpx.Client", _client_factory(httpx.MockTransport(handler))),
        pytest.raises(httpx.HTTPStatusError, match="JWT token expired"),
    ):
        call(client)
    assert len(requests) == 1


_TRACE_ID = "0af7651916cd43dd8448eb211c80319c"


def _multipart(request: httpx.Request) -> tuple[dict[str, str], dict[str, tuple]]:
    """Split a multipart body into text fields and (filename, type, bytes) files."""
    boundary = request.headers["content-type"].split("boundary=")[1].encode()
    fields: dict[str, str] = {}
    files: dict[str, tuple] = {}
    for part in request.content.split(b"--" + boundary)[1:-1]:
        head, _, body = part[2:-2].partition(b"\r\n\r\n")
        head_text = head.decode()
        name = re.search(r'name="([^"]*)"', head_text).group(1)
        filename = re.search(r'filename="([^"]*)"', head_text)
        if filename:
            ctype = re.search(r"Content-Type: (\S+)", head_text).group(1)
            files[name] = (filename.group(1), ctype, body)
        else:
            fields[name] = body.decode()
    return fields, files


@pytest.mark.parametrize("thread_id", ["", "D_9"], ids=["new_thread", "existing"])
@pytest.mark.parametrize(
    ("method", "file_arg", "expected_file"),
    [
        (
            "upload_image",
            {"image": b"\x89PNG\r\n\x1a\n" + b"\x00" * 16},
            ("image.png", "image/png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 16),
        ),
        (
            "upload_binary",
            {"file": b"%PDF-1.4\n%%EOF\n", "filename": "report.pdf"},
            ("report.pdf", "application/pdf", b"%PDF-1.4\n%%EOF\n"),
        ),
    ],
    ids=["upload_image", "upload_binary"],
)
def test_file_upload_forwards_every_argument_to_the_wire(
    louie_client, method, file_arg, expected_file, thread_id
):
    """upload_image/upload_binary hand every argument through _send_file intact."""
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return _reply(
            200, '{"type": "StreamingApiMessageStart", "dthread_id": "D_9"}\n'
        )

    with patch("httpx.Client", _client_factory(httpx.MockTransport(handler))):
        response = getattr(louie_client, method)(
            prompt="Describe it",
            thread_id=thread_id,
            agent="CustomUploadAgent",
            traces=True,
            include_reasoning=True,
            share_mode="Organization",
            name="my-name",
            folder="BOTS/run_1",
            session_trace_id=_TRACE_ID,
            **file_arg,
        )

    assert len(requests) == 1
    request = requests[0]
    assert request.url.path == "/api/chat_upload/"
    assert request.headers["traceparent"].split("-")[1] == _TRACE_ID
    fields, files = _multipart(request)
    expected = {
        "query": "Describe it",
        "agent": "CustomUploadAgent",
        "ignore_traces": "false",
        "include_reasoning": "true",
        "share_mode": "Organization",
    }
    if thread_id:
        expected["dthread_id"] = thread_id
    else:
        expected.update(name="my-name", folder="BOTS/run_1")
    assert fields == expected
    assert files == {"files": expected_file}
    assert response.thread_id == "D_9"
