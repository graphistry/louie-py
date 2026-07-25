"""Integration-credential gating must fail closed.

`load_test_credentials()` used to call `load_dotenv()` unconditionally, so an
operator who cleared every credential variable still got credentials back from
`.env` — and the credentialed fixtures then dialled the real server. These tests
lock the opt-in behaviour in place.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.utils import dotenv_enabled, load_test_credentials, repo_root

pytestmark = pytest.mark.unit

CREDENTIAL_VARS = (
    "GRAPHISTRY_SERVER",
    "GRAPHISTRY_USERNAME",
    "GRAPHISTRY_PASSWORD",
    "GRAPHISTRY_API_VERSION",
    "LOUIE_SERVER",
    "LOUIE_SERVER_URL",
    "LOUIE_URL",
)


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> pytest.MonkeyPatch:
    """No credentials in the environment, and `.env` stubbed to a known payload.

    `load_dotenv()` resolves `.env` from the calling module's directory, not the
    process cwd, so a real file in `tmp_path` would be ignored and the repo's own
    `.env` would win. Stub the loader instead: that tests the contract (is `.env`
    consulted?) without depending on whether a developer has one.
    """
    for name in CREDENTIAL_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("LOUIE_TEST_MODE", raising=False)
    monkeypatch.chdir(tmp_path)

    # Must go through monkeypatch.setenv, not os.environ directly: a direct
    # write is not undone at teardown and leaks GRAPHISTRY_SERVER into every
    # later test in the session, where `Cursor()` then rejects it.
    def fake_load_dotenv(*args: object, **kwargs: object) -> bool:
        monkeypatch.setenv("GRAPHISTRY_SERVER", "dotenv.example.com")
        monkeypatch.setenv("GRAPHISTRY_USERNAME", "dotenv-user")
        monkeypatch.setenv("GRAPHISTRY_PASSWORD", "dotenv-pass")
        monkeypatch.setenv("LOUIE_SERVER", "https://dotenv.example.com")
        return True

    monkeypatch.setattr("tests.utils.load_dotenv", fake_load_dotenv)
    return monkeypatch


def test_dotenv_is_opt_in(clean_env: pytest.MonkeyPatch) -> None:
    assert dotenv_enabled() is False
    clean_env.setenv("LOUIE_TEST_MODE", "integration")
    assert dotenv_enabled() is True


@pytest.mark.parametrize("mode", ["integration", "all", "INTEGRATION", "All"])
def test_integration_modes_enable_dotenv(
    clean_env: pytest.MonkeyPatch, mode: str
) -> None:
    """`all` must opt in too — it runs the integration tests."""
    clean_env.setenv("LOUIE_TEST_MODE", mode)
    assert dotenv_enabled() is True


@pytest.mark.parametrize("mode", ["unit", "", "smoke"])
def test_non_integration_modes_keep_dotenv_off(
    clean_env: pytest.MonkeyPatch, mode: str
) -> None:
    clean_env.setenv("LOUIE_TEST_MODE", mode)
    assert dotenv_enabled() is False
    assert load_test_credentials() is None


def test_conftest_and_utils_share_one_mode_source(
    clean_env: pytest.MonkeyPatch,
) -> None:
    """They previously disagreed about `all`; they must not drift again."""
    from tests.conftest import get_test_mode as conftest_mode
    from tests.conftest import should_run_integration_tests
    from tests.utils import get_test_mode as utils_mode

    assert conftest_mode is utils_mode
    clean_env.setenv("LOUIE_TEST_MODE", "all")
    assert should_run_integration_tests() is True
    assert dotenv_enabled() is True


def test_test_sh_only_loads_dotenv_for_integration_modes() -> None:
    """`scripts/test.sh` used to export .env in every mode, defeating this gate."""
    script = (repo_root() / "scripts" / "test.sh").read_text(encoding="utf-8")
    load_line = next(line for line in script.splitlines() if "-f .env" in line)

    assert "integration" in load_line and "all" in load_line, load_line
    # And the mode must be exported before the gated load reads it.
    assert script.index('export LOUIE_TEST_MODE="$TEST_MODE"') < script.index(load_line)


def test_cleared_environment_yields_no_credentials(
    clean_env: pytest.MonkeyPatch,
) -> None:
    """The regression: .env must not resurrect cleared credentials."""
    assert load_test_credentials() is None
    # And the environment must stay clean, so downstream gating also skips.
    assert not os.getenv("GRAPHISTRY_SERVER")
    assert not os.getenv("LOUIE_SERVER")


def test_integration_mode_reads_dotenv(clean_env: pytest.MonkeyPatch) -> None:
    """Explicit opt-in still works for local integration runs."""
    clean_env.setenv("LOUIE_TEST_MODE", "integration")

    credentials = load_test_credentials()

    assert credentials is not None
    assert credentials["server"] == "dotenv.example.com"


def test_real_environment_wins_without_dotenv(clean_env: pytest.MonkeyPatch) -> None:
    """CI path: real env vars, no .env consulted."""
    clean_env.setenv("GRAPHISTRY_SERVER", "ci.example.com")
    clean_env.setenv("GRAPHISTRY_USERNAME", "ci-user")
    clean_env.setenv("GRAPHISTRY_PASSWORD", "ci-pass")

    credentials = load_test_credentials()

    assert credentials is not None
    assert credentials["server"] == "ci.example.com"


def test_partial_credentials_are_rejected(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("GRAPHISTRY_SERVER", "ci.example.com")
    clean_env.setenv("GRAPHISTRY_USERNAME", "ci-user")
    # password intentionally absent

    assert load_test_credentials() is None
