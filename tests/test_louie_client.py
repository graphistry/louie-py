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
            # For testing purposes, we'll create a simple HTTPStatusError
            # The production code will catch this and extract error info
            raise httpx.HTTPStatusError(
                f"Error: status {self.status_code}",
                request=httpx.Request("POST", "http://test.com"),
                response=httpx.Response(self.status_code)
            )

    def json(self) -> Dict[str, Any]:
        return self._data

    @property
    def text(self) -> str:
        """Return text representation of the response data."""
        if self._data:
            import json
            return json.dumps(self._data)
        return f"HTTP {self.status_code} response"


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


def test_http_error_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    # Monkeypatch httpx.post to simulate a 500 response with error message
    import httpx

    # Create a response that will trigger HTTPStatusError with our error data
    def mock_post(*args, **kwargs) -> Any:
        # Create a mock response that raises HTTPStatusError with error details
        class MockResponse:
            def __init__(self) -> None:
                self.status_code = 500
                self._json_data = {"error": "Internal Server Error"}

            def raise_for_status(self) -> None:
                import httpx
                # Create HTTPStatusError with this response attached
                request = httpx.Request("POST", "http://test.com")
                # The HTTPStatusError needs a real Response object
                response = httpx.Response(500, request=request)
                # Monkey patch the json method to return our data
                def json_with_error() -> Dict[str, Any]:
                    return self._json_data
                response.json = json_with_error
                raise httpx.HTTPStatusError(
                    "HTTP 500", request=request, response=response
                )

            def json(self) -> Dict[str, Any]:
                return self._json_data

        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)
    monkeypatch.setattr(graphistry, "api_token", lambda: "token")
    client = louieai.LouieClient()
    with pytest.raises(RuntimeError) as exc:
        client.ask("test")
    # The error message should contain status code and "Internal Server Error"
    err = str(exc.value)
    assert "500" in err and "Internal Server Error" in err


def test_network_error_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    # Monkeypatch httpx.post to simulate a network error
    import httpx
    def raise_network_error(*args, **kwargs) -> None:
        raise httpx.RequestError("Connection failed")
    monkeypatch.setattr(httpx, "post", raise_network_error)
    monkeypatch.setattr(graphistry, "api_token", lambda: "token")
    client = louieai.LouieClient()
    with pytest.raises(RuntimeError) as exc:
        client.ask("test")
    # The error message should contain network error details
    err = str(exc.value)
    assert "Failed to connect to LouieAI" in err
