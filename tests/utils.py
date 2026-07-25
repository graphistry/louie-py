"""Test utilities for Louie.ai client."""

import os
from pathlib import Path

from dotenv import load_dotenv


def repo_root() -> Path:
    """Repository root, resolved by walking up to the pyproject.toml.

    Deliberately not `Path(__file__).parents[N]`: a hardcoded depth breaks
    silently when a test file moves between directories, and several security
    tests copy scripts out of the root — a wrong root there yields a fixture
    that exercises nothing while still passing.
    """
    for candidate in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise RuntimeError("could not locate repository root (no pyproject.toml found)")


# Modes that are allowed to reach a real server, and therefore to read `.env`.
INTEGRATION_MODES = frozenset({"integration", "all"})


def get_test_mode() -> str:
    """Current test mode. Single source of truth for `LOUIE_TEST_MODE`.

    `tests/conftest.py` imports this rather than re-reading the variable, so the
    two cannot drift (they previously disagreed about the `all` mode).
    """
    return os.environ.get("LOUIE_TEST_MODE", "unit").lower()


def dotenv_enabled() -> bool:
    """True when `.env` may supply integration credentials.

    Loading `.env` unconditionally made it impossible to run the suite without
    credentials: clearing `GRAPHISTRY_*` / `LOUIE_SERVER` in the environment had
    no effect, because `.env` silently put them back and the credentialed
    fixtures then dialled the real server (observed: a ~4 minute hang on a run
    that was explicitly launched with every credential variable unset).

    `.env` is therefore opt-in. Set `LOUIE_TEST_MODE=integration` (or `all`).
    CI is unaffected: it injects real environment variables from secrets and has
    no `.env` file.
    """
    return get_test_mode() in INTEGRATION_MODES


def load_test_credentials() -> dict[str, str] | None:
    """Load test credentials from environment variables.

    Reads the process environment. `.env` is consulted only in an integration
    mode — see :func:`dotenv_enabled`.

    Returns:
        Dictionary with server, username, and password if all are set.
        None if any required credential is missing.
    """
    if dotenv_enabled():
        load_dotenv()

    # Get credentials from environment
    server = os.getenv("GRAPHISTRY_SERVER")
    username = os.getenv("GRAPHISTRY_USERNAME")
    password = os.getenv("GRAPHISTRY_PASSWORD")
    api_version = os.getenv("GRAPHISTRY_API_VERSION", "3")

    # Check if all required credentials are present
    if not all([server, username, password]):
        return None

    return {
        "server": server,
        "username": username,
        "password": password,
        "api_version": int(api_version),
    }


def skip_if_no_credentials(test_func):
    """Decorator to skip tests if credentials are not available.

    Use this for integration tests that require real Louie instance access.
    """
    import pytest

    def wrapper(*args, **kwargs):
        if load_test_credentials() is None:
            pytest.skip(
                "Test credentials not configured. "
                "Set GRAPHISTRY_SERVER, GRAPHISTRY_USERNAME, "
                "and GRAPHISTRY_PASSWORD environment variables."
            )
        return test_func(*args, **kwargs)

    return wrapper
