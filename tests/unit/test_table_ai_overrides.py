from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest
from typing_extensions import Self

from louieai._client import LouieClient, Response
from louieai._table_ai import TableAIOverrides
from louieai._upload import UploadClient


class DummyResponse:
    def __init__(self, payload: list[dict[str, Any]]) -> None:
        self._payload = payload
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> list[dict[str, Any]]:
        return self._payload


@pytest.fixture
def mock_client(monkeypatch: pytest.MonkeyPatch) -> LouieClient:
    client = LouieClient(server_url="http://test")
    httpx_mock = MagicMock()
    client._client = httpx_mock  # type: ignore[attr-defined]
    monkeypatch.setattr(client, "_get_headers", lambda: {})  # avoid auth
    monkeypatch.setattr(client, "_fetch_dataframe_arrow", lambda *args, **kwargs: None)
    return client


def test_add_cell_with_table_ai_overrides(mock_client: LouieClient) -> None:
    overrides_model = TableAIOverrides(
        semantic_mode="map",
        output_column="semantic_map",
        ask_model="gpt-4o-mini",
        evidence_model="gpt-4o",
        options={"max_rows": 5},
    )
    singleshot_payload = [
        {"dthread_id": "D123"},
        {"payload": {"id": "elem-1", "type": "TextElement", "text": "hi"}},
    ]
    mock_post = MagicMock(return_value=DummyResponse(singleshot_payload))
    mock_client._client.post = mock_post  # type: ignore[attr-defined]

    response = mock_client.add_cell(
        "",
        "Summarize rows",
        agent="TableAIAgent",
        table_ai_overrides=overrides_model,
    )

    request_call = mock_post.call_args
    assert request_call is not None
    url = request_call[0][0]
    params = request_call[1]["params"]
    assert url.endswith("/api/chat_singleshot/")
    assert params["table_ai_semantic_mode"] == "map"
    assert json.loads(params["table_ai_options"]) == {"max_rows": 5}
    assert response.thread_id == "D123"
    assert response.elements[0]["text"] == "hi"


def test_add_cell_with_mapping_overrides(mock_client: LouieClient) -> None:
    mock_post = MagicMock(return_value=DummyResponse([]))
    mock_client._client.post = mock_post  # type: ignore[attr-defined]

    response = mock_client.add_cell(
        "",
        "Summarize rows",
        table_ai_overrides={
            "semantic_mode": "reduce",
            "output_column": "semantic_reduce",
            "ask_model": "gpt-4.1",
            "options": {"foo": "bar"},
        },
    )

    request_call = mock_post.call_args
    assert request_call is not None
    params = request_call[1]["params"]
    assert params["table_ai_semantic_mode"] == "reduce"
    assert params["table_ai_output_column"] == "semantic_reduce"
    assert params["table_ai_ask_model"] == "gpt-4.1"
    assert json.loads(params["table_ai_options"]) == {"foo": "bar"}
    assert response.thread_id == ""


def test_add_cell_with_legacy_kwargs(mock_client: LouieClient) -> None:
    mock_post = MagicMock(return_value=DummyResponse([]))
    mock_client._client.post = mock_post  # type: ignore[attr-defined]

    response = mock_client.add_cell(
        "",
        "Summarize rows",
        table_ai_semantic_mode="map",
        table_ai_output_column="semantic_map",
        table_ai_options={"limit": 5},
    )

    params = mock_post.call_args[1]["params"]
    assert params["table_ai_semantic_mode"] == "map"
    assert params["table_ai_output_column"] == "semantic_map"
    assert json.loads(params["table_ai_options"]) == {"limit": 5}
    assert response.thread_id == ""


def test_upload_dataframe_with_table_ai_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = LouieClient(server_url="http://test")
    upload_client = UploadClient(client)
    monkeypatch.setattr(client, "_get_headers", lambda: {})  # avoid auth

    class FakeStreamResponse:
        def __init__(self) -> None:
            self.status_code = 200

        def raise_for_status(self) -> None:
            return None

        def iter_lines(self):  # type: ignore[override]
            yield json.dumps({"dthread_id": "D456"})
            yield json.dumps(
                {"payload": {"id": "elem-1", "type": "TextElement", "text": "done"}}
            )

    class FakeStreamContext:
        def __enter__(self) -> FakeStreamResponse:
            return FakeStreamResponse()

        def __exit__(self, *args: object) -> None:
            return None

    class FakeHttpxClient:
        def __init__(self, timeout: Any) -> None:
            self.last_request: dict[str, Any] | None = None

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def stream(
            self,
            method: str,
            url: str,
            *,
            headers: Any,
            data: Any,
            files: Any,
        ) -> FakeStreamContext:
            self.last_request = {
                "method": method,
                "url": url,
                "headers": headers,
                "data": data,
                "files": files,
            }
            return FakeStreamContext()

    fake_client = FakeHttpxClient(timeout=None)
    monkeypatch.setattr("louieai._upload.httpx.Client", lambda timeout: fake_client)
    monkeypatch.setattr(client, "_fetch_dataframe_arrow", lambda *args, **kwargs: None)

    df = pd.DataFrame({"value": [1, 2]})
    response = upload_client.upload_dataframe(
        prompt="Summarize",
        df=df,
        table_ai_overrides=TableAIOverrides(
            semantic_mode="map",
            output_column="semantic_map",
            ask_model="gpt-4o-mini",
            evidence_model="gpt-4o",
            options={"max_rows": 5},
        ),
    )

    assert response.thread_id == "D456"
    assert response.elements[0]["text"] == "done"

    assert fake_client.last_request is not None
    data = fake_client.last_request["data"]
    assert data["table_ai_semantic_mode"] == "map"
    assert json.loads(data["table_ai_options"]) == {"max_rows": 5}


def test_upload_dataframe_with_legacy_kwargs(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LouieClient(server_url="http://test")
    upload_client = UploadClient(client)
    monkeypatch.setattr(client, "_get_headers", lambda: {})

    class FakeStreamResponse:
        def __init__(self) -> None:
            self.status_code = 200

        def raise_for_status(self) -> None:
            return None

        def iter_lines(self):  # type: ignore[override]
            yield json.dumps({"dthread_id": "D999"})
            yield json.dumps(
                {"payload": {"id": "elem-1", "type": "TextElement", "text": "done"}}
            )

    class FakeStreamContext:
        def __enter__(self) -> FakeStreamResponse:
            return FakeStreamResponse()

        def __exit__(self, *args: object) -> None:
            return None

    class FakeHttpxClient:
        def __init__(self, timeout: Any) -> None:
            self.last_request: dict[str, Any] | None = None

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def stream(
            self,
            method: str,
            url: str,
            *,
            headers: Any,
            data: Any,
            files: Any,
        ) -> FakeStreamContext:
            self.last_request = {
                "method": method,
                "url": url,
                "headers": headers,
                "data": data,
                "files": files,
            }
            return FakeStreamContext()

    fake_client = FakeHttpxClient(timeout=None)
    monkeypatch.setattr("louieai._upload.httpx.Client", lambda timeout: fake_client)
    monkeypatch.setattr(client, "_fetch_dataframe_arrow", lambda *args, **kwargs: None)

    df = pd.DataFrame({"value": [1, 2]})
    response = upload_client.upload_dataframe(
        prompt="Summarize",
        df=df,
        table_ai_semantic_mode="reduce",
        table_ai_ask_options={"temperature": 0.1},
    )

    assert response.thread_id == "D999"
    assert fake_client.last_request is not None
    data = fake_client.last_request["data"]
    assert data["table_ai_semantic_mode"] == "reduce"
    assert json.loads(data["table_ai_ask_options"]) == {"temperature": 0.1}


def test_create_thread_forwards_table_ai_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = LouieClient(server_url="http://test")
    overrides = TableAIOverrides(semantic_mode="map")
    captured: dict[str, Any] = {}

    def fake_add_cell(
        thread_id: str,
        prompt: str,
        agent: str = "",
        *,
        table_ai_overrides: TableAIOverrides | None = None,
        **kwargs: Any,
    ) -> Response:
        captured.update(
            {
                "thread_id": thread_id,
                "prompt": prompt,
                "agent": agent,
                "table_ai_overrides": table_ai_overrides,
                "kwargs": kwargs,
            }
        )
        return Response(thread_id="D789", elements=[])

    monkeypatch.setattr(client, "add_cell", fake_add_cell)

    thread = client.create_thread(
        name="Test",
        initial_prompt="hello",
        agent="TableAIAgent",
        table_ai_overrides=overrides,
        table_ai_semantic_mode="map",
    )

    assert thread.id == "D789"
    assert thread.name == "Test"
    assert captured["table_ai_overrides"] is overrides
    assert captured["kwargs"]["table_ai_semantic_mode"] == "map"
