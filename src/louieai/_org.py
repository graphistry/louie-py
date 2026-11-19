"""The Louie organization a request acts in: the ``X-Graphistry-Org`` header.

A client's ``default_org`` applies to every request; a method's ``org=``
overrides it for that call, including the requests that call makes on its own
(dataframe fetches, streaming).
"""

from __future__ import annotations

import functools
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

_request_org: ContextVar[str | None] = ContextVar("louieai_request_org", default=None)

NO_ORG_DEPRECATION = (
    "Requests without an organization are deprecated: pass default_org='<org slug>' "
    "when you log in, e.g. louie(..., default_org='my-org'), or org='<org slug>' on a "
    "call. A future release will require it."
)


@contextmanager
def request_org(org: str | None) -> Iterator[None]:
    """Requests made inside act in ``org``; ``None`` keeps the enclosing choice."""
    if org is None:
        yield
        return
    token = _request_org.set(org)
    try:
        yield
    finally:
        _request_org.reset(token)


def current_request_org() -> str | None:
    """The ``org=`` of the call in progress, if it named one."""
    return _request_org.get()


def uses_request_org(method: Callable[P, R]) -> Callable[P, R]:
    """Run ``method`` in the org its ``org=`` keyword names."""

    @functools.wraps(method)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        org = kwargs.get("org")
        with request_org(org if isinstance(org, str) else None):
            return method(*args, **kwargs)

    return wrapper
