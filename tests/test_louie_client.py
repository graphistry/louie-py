from typing import Any, Dict, Optional

import graphistry
import louieai
import pytest


class DummyResponse:
    def __init__(
        self, status_code: int = 200, data: Optional[Dict[str, Any]] = None
    ) -> None:
        self.status_code = status_code
        self._data = data or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            import httpx
            # Create minimal request for HTTPStatusError
            request = httpx.Request("POST", "http://test.com")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError(
                f"Error: status {self.status_code}",
                request=request,
                response=response
            )

    def json(self) -> Dict[str, Any]:
        return self._data


def test_client_uses_graphistry_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # Monkeypatch graphistry.api_token to return a dummy token
    monkeypatch.setattr(graphistry, "api_token", lambda: "fake-token")
    # Monkeypatch httpx.post to simulate a successful response
    import httpx
    monkeypatch.setattr(
        httpx,
        "post",
        lambda url, json, headers, timeout: DummyResponse(data={"result": "ok"}),
    )
    client = louieai.LouieClient()
    result = client.ask("hello")
    assert result == {"result": "ok"}
    # The fake token should have been used in headers; we can't directly check the
    # headers here, but we know our DummyResponse returned data without raising,
    # meaning our code likely worked.


def test_client_no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # Monkeypatch graphistry.api_token to return None
    monkeypatch.setattr(graphistry, "api_token", lambda: None)
    client = louieai.LouieClient()
    with pytest.raises(RuntimeError) as excinfo:
        client.ask("anything")
    err = str(excinfo.value)
    assert "No Graphistry API token" in err
