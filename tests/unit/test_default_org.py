"""default_org at login, org= per call, and the warning for requests without either."""

from __future__ import annotations

import json
import warnings
from collections.abc import Iterator
from unittest.mock import MagicMock

import httpx
import pytest

import louieai
import louieai._client as client_module
from louieai._client import LouieClient
from louieai._org import NO_ORG_DEPRECATION, current_request_org, request_org
from louieai.notebook.cursor import Cursor

SERVER = "https://louie.example.com"
ORG_HEADER = "X-Graphistry-Org"


class Recorder:
    """Every request the client sends, answered like a minimal Louie server."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path
        if path == "/api/chat/":
            lines = [
                {"dthread_id": "D1"},
                {"payload": {"id": "B1", "type": "DfElement"}},
            ]
            return httpx.Response(200, text="\n".join(json.dumps(x) for x in lines))
        if path == "/api/dthreads":
            return httpx.Response(200, json={"data": [{"id": "D1", "name": "t"}]})
        return httpx.Response(404, json={"detail": "not found"})

    def orgs(self) -> list[tuple[str, str | None]]:
        return [(r.url.path, r.headers.get(ORG_HEADER)) for r in self.requests]


@pytest.fixture
def server(monkeypatch: pytest.MonkeyPatch) -> Recorder:
    recorder = Recorder()
    real_client = httpx.Client

    def client_factory(*_args: object, **kwargs: object) -> httpx.Client:
        return real_client(transport=httpx.MockTransport(recorder))

    monkeypatch.setattr(client_module.httpx, "Client", client_factory)
    return recorder


@pytest.fixture
def no_warnings() -> Iterator[list[warnings.WarningMessage]]:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        yield caught


def org_warnings(
    caught: list[warnings.WarningMessage],
) -> list[warnings.WarningMessage]:
    return [w for w in caught if str(w.message) == NO_ORG_DEPRECATION]


def client(**kwargs: object) -> LouieClient:
    return LouieClient(server_url=SERVER, token="t", **kwargs)  # type: ignore[arg-type]


def test_default_org_goes_on_every_request(server: Recorder) -> None:
    lc = client(default_org="acme")
    lc.list_threads()
    lc.add_cell("", "q")
    assert {org for _, org in server.orgs()} == {"acme"}


def test_org_on_a_call_wins_for_that_call_and_its_own_requests(
    server: Recorder,
) -> None:
    lc = client(default_org="acme")
    lc.add_cell("", "q", org="globex")  # also fetches its dataframe
    lc.list_threads()
    assert server.orgs() == [
        ("/api/chat/", "globex"),
        ("/api/dthread/D1/df/block/B1/arrow", "globex"),
        ("/api/dthreads", "acme"),
    ]


def test_create_thread_passes_its_org_to_the_cell_it_adds(server: Recorder) -> None:
    client(default_org="acme").create_thread(initial_prompt="q", org="globex")
    assert {org for _, org in server.orgs()} == {"globex"}


def test_org_names_are_sent_as_slugs(server: Recorder) -> None:
    client(default_org="My Org").list_threads(org="Other Team")
    assert server.orgs() == [("/api/dthreads", "other-team")]


def test_register_sets_default_org_without_passing_it_on() -> None:
    lc = client()
    lc._auth_manager = MagicMock()
    lc.register(api_key="k", default_org="acme")
    lc._auth_manager.register.assert_called_once_with(api_key="k")
    assert lc._default_org == "acme"


def test_org_name_alone_still_sends_the_header_without_a_warning(
    server: Recorder, no_warnings: list[warnings.WarningMessage]
) -> None:
    lc = client()
    lc._auth_manager._credentials["org_name"] = "acme"
    lc.list_threads()
    assert server.orgs() == [("/api/dthreads", "acme")]
    assert org_warnings(no_warnings) == []


def test_requests_without_an_org_warn_once_per_client(
    server: Recorder, no_warnings: list[warnings.WarningMessage]
) -> None:
    lc = client()
    lc.list_threads()
    lc.list_threads()
    assert server.orgs() == [("/api/dthreads", None), ("/api/dthreads", None)]
    (warning,) = org_warnings(no_warnings)
    assert warning.category is FutureWarning


def test_an_org_on_the_call_avoids_the_warning(
    server: Recorder, no_warnings: list[warnings.WarningMessage]
) -> None:
    client().list_threads(org="acme")
    assert org_warnings(no_warnings) == []


def test_anonymous_logins_do_not_warn(
    server: Recorder, no_warnings: list[warnings.WarningMessage]
) -> None:
    LouieClient(server_url=SERVER, token="t", anonymous=True).list_threads()
    assert server.orgs() == [("/api/dthreads", None)]
    assert org_warnings(no_warnings) == []


def test_request_org_nests_and_restores() -> None:
    with request_org("acme"):
        with request_org(None):
            assert current_request_org() == "acme"
        with request_org("globex"):
            assert current_request_org() == "globex"
        assert current_request_org() == "acme"
    assert current_request_org() is None


def test_the_notebook_cursor_runs_a_query_in_its_org() -> None:
    lc = MagicMock(spec=LouieClient)
    seen: list[str | None] = []
    lc.add_cell.side_effect = lambda **_kw: (
        seen.append(current_request_org()) or client_module.Response("D1", [])
    )
    lui = Cursor(client=lc)
    lui._in_jupyter = lambda: False  # type: ignore[method-assign]
    lui("q", org="globex")
    lui("q")
    assert seen == ["globex", None]


def test_the_louie_factory_takes_default_org() -> None:
    lui = louieai.louie(server_url=SERVER, token="t", default_org="acme")
    assert lui._client._default_org == "acme"
