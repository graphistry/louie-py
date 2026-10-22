"""Server error details survive streamed requests (issue #52).

Uses real httpx streaming over a MockTransport: with plain
``response.raise_for_status()`` the body of a streamed error is closed before
callers can read it, so ``agent="SplunkAgent"`` surfaced as a bare
``400 Bad Request`` instead of the server's ``Invalid agent 'SplunkAgent'``.
"""

from unittest.mock import Mock, patch

import httpx
import pandas as pd
import pytest

from louieai._client import LouieClient
from louieai._http import error_detail, raise_for_status

_RealClient = httpx.Client
INVALID_AGENT = {"detail": "Invalid agent 'SplunkAgent'"}


def _transport(status: int, **kwargs) -> httpx.MockTransport:
    return httpx.MockTransport(lambda request: httpx.Response(status, **kwargs))


def _client_factory(transport: httpx.MockTransport):
    """Stand-in for ``httpx.Client(...)`` that routes to ``transport``."""

    def make(*args, **kwargs):
        kwargs.pop("transport", None)
        return _RealClient(*args, transport=transport, **kwargs)

    return make


def _streamed_error(status: int, **kwargs) -> pytest.ExceptionInfo:
    with (
        _RealClient(transport=_transport(status, **kwargs)) as client,
        client.stream("POST", "https://louie.test/api/chat/") as response,
        pytest.raises(httpx.HTTPStatusError) as excinfo,
    ):
        raise_for_status(response)
    return excinfo


class TestRaiseForStatus:
    def test_streamed_json_detail_in_message(self):
        excinfo = _streamed_error(400, json=INVALID_AGENT)
        message = str(excinfo.value)
        assert message.startswith("Client error '400 Bad Request'")
        assert "Server detail: Invalid agent 'SplunkAgent'" in message

    def test_body_stays_readable_after_stream_closes(self):
        excinfo = _streamed_error(400, json=INVALID_AGENT)
        assert excinfo.value.response.status_code == 400
        assert excinfo.value.response.json() == INVALID_AGENT

    def test_baseline_plain_raise_for_status_omits_detail(self):
        """Documents the bug: httpx's own message never includes the body.

        (Against a real server the closed stream also makes the body unreadable
        afterwards -- ``httpx.StreamClosed``; MockTransport buffers it, so that
        half is verified live, not here.)
        """
        with (
            _RealClient(transport=_transport(400, json=INVALID_AGENT)) as client,
            client.stream("POST", "https://louie.test/api/chat/") as response,
            pytest.raises(httpx.HTTPStatusError) as excinfo,
        ):
            response.raise_for_status()
        assert "Invalid agent" not in str(excinfo.value)

    def test_non_json_body_used_verbatim(self):
        excinfo = _streamed_error(502, text="upstream unavailable")
        assert "Server detail: upstream unavailable" in str(excinfo.value)

    def test_structured_detail_is_serialized(self):
        detail = [{"loc": ["query", "query"], "msg": "field required"}]
        excinfo = _streamed_error(422, json={"detail": detail})
        assert '"msg": "field required"' in str(excinfo.value)

    def test_empty_body_keeps_original_message(self):
        excinfo = _streamed_error(500)
        assert "Server detail" not in str(excinfo.value)

    def test_success_does_not_raise(self):
        with (
            _RealClient(transport=_transport(200, text="{}")) as client,
            client.stream("POST", "https://louie.test/api/chat/") as response,
        ):
            raise_for_status(response)

    def test_long_detail_truncated(self):
        assert len(error_detail(httpx.Response(400, text="x" * 5000))) == 500


@pytest.fixture
def louie_client():
    graphistry_client = Mock()
    graphistry_client.api_token = Mock(return_value="fake-token")
    return LouieClient(
        server_url="https://louie.test", graphistry_client=graphistry_client
    )


class TestCallSitesSurfaceDetail:
    """Each streamed entry point reports the server's reason."""

    def test_add_cell(self, louie_client):
        with (
            patch("httpx.Client", _client_factory(_transport(400, json=INVALID_AGENT))),
            pytest.raises(httpx.HTTPStatusError, match="Invalid agent 'SplunkAgent'"),
        ):
            louie_client.add_cell("", "hi", agent="SplunkAgent")

    def test_notebook_stream_response(self, louie_client):
        from louieai.notebook.streaming import stream_response

        with (
            patch("httpx.Client", _client_factory(_transport(400, json=INVALID_AGENT))),
            pytest.raises(httpx.HTTPStatusError, match="Invalid agent 'SplunkAgent'"),
        ):
            stream_response(louie_client, "", "hi", agent="SplunkAgent")

    def test_upload_dataframe(self, louie_client):
        detail = {"detail": "Invalid agent 'UploadAgent'"}
        with (
            patch("httpx.Client", _client_factory(_transport(400, json=detail))),
            pytest.raises(httpx.HTTPStatusError, match="Invalid agent 'UploadAgent'"),
        ):
            louie_client.upload_dataframe(
                "hi", pd.DataFrame({"a": [1]}), agent="UploadAgent"
            )
