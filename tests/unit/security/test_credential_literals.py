"""Regression tests for the deterministic Graphistry personal-key gate.

Fixtures are assembled at runtime from fragments so this file never itself
contains a credential-shaped literal that the checker would flag. Every test
asserts the checker's output does not echo the value it rejected.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.utils import repo_root

pytestmark = pytest.mark.unit

REPO_ROOT = repo_root()
CHECKER = REPO_ROOT / "scripts" / "ci" / "check_credential_literals.py"


def _load_checker():
    """Import the stdlib-only checker module for white-box assertions."""
    spec = importlib.util.spec_from_file_location("_cred_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_is_placeholder = _load_checker()._is_placeholder

# Built at runtime: a 10-char id shape and a 16-char secret shape. Both mix
# letters and digits, as the real key formats do.
FAKE_ID = "A1B2C3" + "D4E5"  # pragma: allowlist secret
FAKE_SECRET = "A1B2C3D4" + "E5F6G7H8"  # pragma: allowlist secret
KEY_ID = "personal_key_" + "id"  # pragma: allowlist secret
KEY_SECRET = "personal_key_" + "secret"  # pragma: allowlist secret

# Entropy-boundary fixtures, assembled so no scannable literal exists here.
TOO_SHORT = "AB" + "1234567"
LOW_DISTINCT = "ab" * 7
ABOVE_FLOOR = "abcdef" + "123456"


# Explicit parametrize ids. Without these, pytest -v composes the id from the
# parameter *values*, printing credential-shaped fixtures into public CI logs —
# harmless for these fakes, but the wrong habit for a security suite.
CONTEXT_IDS = [
    "bare",
    "annotated",
    "dict",
    "kwarg",
    "getenv",
    "unrelated",
    "single_quoted",
    "dotenv",
    "shell_export",
    "yaml",
    "markdown",
    "md_fence",
]
OFFSHAPE_IDS = ["bare", "prefixed", "getenv", "dict", "yaml", "annotated"]
PLACEHOLDER_IDS = [
    "angle_id",
    "angle_secret",
    "env_var",
    "pk_mock",
    "test_mock",
    "filler",
    "empty",
    "fake_substring",
    "example_substring",
]


def run_checker(
    *args: str, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        capture_output=True,
        check=False,
        text=True,
        cwd=cwd,
    )


def assert_rejected(result: subprocess.CompletedProcess[str], *secrets: str) -> None:
    """Checker failed, said something useful, and leaked nothing."""
    assert result.returncode == 1, result.stderr
    assert "hard-coded" in result.stderr
    for secret in secrets:
        assert secret not in result.stdout
        assert secret not in result.stderr


def assert_accepted(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


def write(tmp_path: Path, name: str, body: str) -> Path:
    candidate = tmp_path / name
    candidate.write_text(body, encoding="utf-8")
    return candidate


# --- value-shape: context-free, so quoting and file format must not matter ---


@pytest.mark.parametrize(
    ("name", "body"),
    [
        ("bare.py", f'{KEY_SECRET} = "{FAKE_SECRET}"'),
        ("annotated.py", f'{KEY_SECRET}: str = "{FAKE_SECRET}"'),
        ("dict.py", f'creds = {{"{KEY_SECRET}": "{FAKE_SECRET}"}}'),
        ("kwarg.py", f'register({KEY_SECRET}="{FAKE_SECRET}")'),
        ("getenv.py", f'os.getenv("PERSONAL_KEY_SECRET", "{FAKE_SECRET}")'),
        ("unrelated.py", f'blob = "{FAKE_SECRET}"'),
        ("single_quoted.py", f"{KEY_SECRET} = '{FAKE_SECRET}'"),
        # Unquoted forms — the .env / shell / YAML paths DEVELOP.md documents.
        (".env", f"GRAPHISTRY_PERSONAL_KEY_SECRET={FAKE_SECRET}"),
        ("export.sh", f"export GRAPHISTRY_PERSONAL_KEY_SECRET={FAKE_SECRET}"),
        ("conf.yml", f"{KEY_SECRET}: {FAKE_SECRET}"),
        ("notes.md", f"Use {FAKE_SECRET} as the secret."),
        ("fence.md", f'```python\n{KEY_SECRET} = "{FAKE_SECRET}"\n```'),
    ],
    ids=CONTEXT_IDS,
)
def test_rejects_credential_shape_in_any_context(
    tmp_path: Path, name: str, body: str
) -> None:
    """The old key-name regex missed most of these; the shape rule must not."""
    assert_rejected(run_checker(str(write(tmp_path, name, body))), FAKE_SECRET)


def test_rejects_shape_inside_notebook_json(tmp_path: Path) -> None:
    """.ipynb stores source with escaped quotes, so quote-anchored rules miss it.

    The repo's own tutorial notebooks already contain `personal_key_secret = ...`
    cells, which is exactly where an accidental paste would land.
    """
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "source": [f'{KEY_SECRET} = "{FAKE_SECRET}"\n'],
                "outputs": [],
                "execution_count": None,
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    candidate = write(tmp_path, "nb.ipynb", json.dumps(notebook, indent=1))

    assert_rejected(run_checker(str(candidate)), FAKE_SECRET)


def test_rejects_both_id_and_secret_shapes(tmp_path: Path) -> None:
    candidate = write(
        tmp_path, "pair.py", f'{KEY_ID} = "{FAKE_ID}"\n{KEY_SECRET} = "{FAKE_SECRET}"\n'
    )

    result = run_checker(str(candidate))

    assert_rejected(result, FAKE_ID, FAKE_SECRET)
    assert result.stderr.count("hard-coded") == 2


@pytest.mark.parametrize(
    "word",
    ["PRODUCTION", "PROCESSING", "IDENTIFIER", "LINESTRING", "ABCDEFGHIJKLMNOP"],
)
def test_accepts_allcaps_words_without_digits(tmp_path: Path, word: str) -> None:
    """A hard gate that trips on `status = "PROCESSING"` would be unusable."""
    assert_accepted(run_checker(str(write(tmp_path, "enum.py", f'x = "{word}"'))))


def test_accepts_lowercase_shape(tmp_path: Path) -> None:
    """The shape is uppercase; a lowercase look-alike must not trip it."""
    lowered = FAKE_SECRET.lower()
    assert_accepted(run_checker(str(write(tmp_path, "low.py", f'x = "{lowered}"'))))


def test_allowlist_pragma_suppresses(tmp_path: Path) -> None:
    body = f'x = "{FAKE_SECRET}"  # pragma: allowlist secret'
    assert_accepted(run_checker(str(write(tmp_path, "ok.py", body))))


# --- key-context: forward compatibility for other key formats ----------------


OFFSHAPE = "gk-live-" + "9f3a2b7c1d4e"  # pragma: allowlist secret


@pytest.mark.parametrize(
    ("name", "body"),
    [
        ("bare.py", f'{KEY_SECRET} = "{OFFSHAPE}"'),
        ("prefixed.py", f'GRAPHISTRY_PERSONAL_KEY_SECRET = "{OFFSHAPE}"'),
        ("getenv.py", f'os.getenv("GRAPHISTRY_PERSONAL_KEY_SECRET", "{OFFSHAPE}")'),
        ("dict.py", f'creds = {{"{KEY_SECRET}": "{OFFSHAPE}"}}'),
        ("conf.yml", f'{KEY_SECRET}: "{OFFSHAPE}"'),
        ("annotated.py", f'{KEY_SECRET}: str = "{OFFSHAPE}"'),
    ],
    ids=OFFSHAPE_IDS,
)
def test_rejects_offshape_value_under_key_name(
    tmp_path: Path, name: str, body: str
) -> None:
    """A future key format still trips the contextual net, whatever the spelling."""
    result = run_checker(str(write(tmp_path, name, body)))

    assert_rejected(result, OFFSHAPE)
    assert "key-context" in result.stderr


@pytest.mark.parametrize(
    "value",
    [
        "correcthorsebatterystaple",  # alphabetic-only passphrase
        "0123456789012345",  # numeric-only key id
    ],
)
def test_key_context_accepts_alpha_only_and_digit_only_secrets(
    tmp_path: Path, value: str
) -> None:
    """Requiring letter AND digit vetoed these realistic formats."""
    body = f'{KEY_SECRET} = "{value}"'
    assert run_checker(str(write(tmp_path, "f.py", body))).returncode == 1


@pytest.mark.parametrize(
    "value",
    [
        TOO_SHORT,  # 9 chars: below the length floor
        LOW_DISTINCT,
    ],
)
def test_key_context_accepts_low_entropy_values(tmp_path: Path, value: str) -> None:
    """Pins `_looks_like_secret` itself, not `_is_placeholder`.

    These deliberately avoid every placeholder marker — an earlier version used
    `"SHORTMOCK"` and `"aaaaaa"`, which `_is_placeholder` rejects first ("mock"
    is a marker substring; `aaaaaa` is single-character filler), so the entropy
    thresholds were never exercised and both floors could be mutated to 1 with
    the suite still green.
    """
    assert not _is_placeholder(value), f"{value!r} must not be a placeholder"
    body = f'{KEY_SECRET} = "{value}"'
    assert_accepted(run_checker(str(write(tmp_path, "f.py", body))))


def test_key_context_rejects_just_above_the_entropy_floor(tmp_path: Path) -> None:
    """The other side of the boundary, so the floors cannot simply be raised."""
    value = ABOVE_FLOOR
    assert not _is_placeholder(value)
    assert_rejected(
        run_checker(str(write(tmp_path, "f.py", f'{KEY_SECRET} = "{value}"'))), value
    )


# --- value-shape boundary: the base64 lookarounds --------------------------


@pytest.mark.parametrize("boundary", ["+", "/", "="])
def test_shape_bounded_by_base64_chars_is_ignored(
    tmp_path: Path, boundary: str
) -> None:
    """A 10/16-char run inside a base64 blob is not a credential.

    Embedded PNG data URIs in `.ipynb` produce these at roughly one per 400 KB,
    and a data URI has nowhere to put a `# pragma` escape.
    """
    body = f"data = 'xx{boundary}{FAKE_SECRET}{boundary}yy'"
    assert_accepted(run_checker(str(write(tmp_path, "nb.txt", body))))


def test_shape_preceded_by_equals_is_still_caught(tmp_path: Path) -> None:
    """`=` is base64 padding only when trailing; `.env` uses it as a separator."""
    body = f"GRAPHISTRY_PERSONAL_KEY_SECRET={FAKE_SECRET}"
    assert_rejected(run_checker(str(write(tmp_path, ".env", body))), FAKE_SECRET)


def test_no_false_positives_on_real_base64(tmp_path: Path) -> None:
    """Regression guard for the measurement the lookarounds were tuned against."""
    import base64
    import random

    rng = random.Random(20260725)
    blob = base64.b64encode(bytes(rng.randrange(256) for _ in range(60_000))).decode()
    candidate = write(tmp_path, "blob.txt", f'img = "{blob}"')

    assert_accepted(run_checker(str(candidate)))


# --- accepted: placeholders and mock values ---------------------------------


@pytest.mark.parametrize(
    "body",
    [
        f'{KEY_ID} = "<your-personal-key-id>"',
        f'{KEY_SECRET} = "<your-personal-key-secret>"',
        f'{KEY_SECRET} = "${{PERSONAL_KEY_SECRET}}"',
        f'{KEY_ID} = "pk_id"',
        f'{KEY_SECRET} = "test-secret"',
        f'{KEY_SECRET} = "XXXXXXXXXXXXXXXX"',
        f'{KEY_SECRET} = ""',
        # substring placeholder markers, not just prefixes
        f'{KEY_SECRET} = "my-fake-key-1234"',
        f'{KEY_SECRET} = "some-example-value-9"',
    ],
    ids=PLACEHOLDER_IDS,
)
def test_accepts_placeholders_and_mocks(tmp_path: Path, body: str) -> None:
    assert_accepted(run_checker(str(write(tmp_path, "safe.py", body))))


def test_skips_binary_files(tmp_path: Path) -> None:
    """Real quoted content, so only the binary guard can prevent a finding."""
    candidate = tmp_path / "blob.bin"
    candidate.write_bytes(
        b"\x00\x01" + f'{KEY_SECRET} = "{FAKE_SECRET}"'.encode() + b"\x00"
    )

    assert_accepted(run_checker(str(candidate)))


# --- index vs worktree ------------------------------------------------------


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "t@example.com"],
        ["git", "config", "user.name", "t"],
    ):
        subprocess.run(command, cwd=repo, check=True, capture_output=True)
    return repo


def test_staged_mode_catches_credential_cleaned_from_worktree(git_repo: Path) -> None:
    """The exact evasion --staged exists to stop.

    Stage a credential, then clean the working tree. A worktree scan passes;
    the staged scan must still fail, because the commit would carry the secret.
    """
    target = git_repo / "config.py"
    target.write_text(f'{KEY_SECRET} = "{FAKE_SECRET}"\n', encoding="utf-8")
    subprocess.run(["git", "add", "config.py"], cwd=git_repo, check=True)
    target.write_text(
        f'{KEY_SECRET} = "<your-personal-key-secret>"\n', encoding="utf-8"
    )

    assert_accepted(run_checker(cwd=git_repo))
    assert_rejected(run_checker("--staged", cwd=git_repo), FAKE_SECRET)


def test_staged_mode_catches_rename_plus_edit(git_repo: Path) -> None:
    """Rename detection reports `R`, which --diff-filter=ACM drops.

    Without --no-renames this is a working pre-commit bypass.
    """
    original = git_repo / "clean.py"
    original.write_text("x = 1\n" * 20, encoding="utf-8")
    subprocess.run(["git", "add", "clean.py"], cwd=git_repo, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "seed"], cwd=git_repo, check=True, capture_output=True
    )

    subprocess.run(["git", "mv", "clean.py", "config.py"], cwd=git_repo, check=True)
    renamed = git_repo / "config.py"
    renamed.write_text(
        renamed.read_text(encoding="utf-8") + f'{KEY_SECRET} = "{FAKE_SECRET}"\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=git_repo, check=True)

    assert_rejected(run_checker("--staged", cwd=git_repo), FAKE_SECRET)


def test_worktree_mode_scans_tracked_files(git_repo: Path) -> None:
    target = git_repo / "config.py"
    target.write_text(f'{KEY_SECRET} = "{FAKE_SECRET}"\n', encoding="utf-8")
    subprocess.run(["git", "add", "config.py"], cwd=git_repo, check=True)

    assert_rejected(run_checker(cwd=git_repo), FAKE_SECRET)


def test_clean_repo_passes_both_modes(git_repo: Path) -> None:
    target = git_repo / "config.py"
    target.write_text(f'{KEY_ID} = "<your-personal-key-id>"\n', encoding="utf-8")
    subprocess.run(["git", "add", "config.py"], cwd=git_repo, check=True)

    assert_accepted(run_checker(cwd=git_repo))
    assert_accepted(run_checker("--staged", cwd=git_repo))


# --- internal-host rule -----------------------------------------------------
#
# The local .git/hooks/pre-commit enumerated two specific dev hostnames, but it
# is untracked: no other contributor has it and CI never runs it. The rule here
# is domain-level and tracked, so it is enforced for everyone and covers
# subdomains nobody has thought of yet.


# Assembled at runtime so this file carries no internal hostname of its own —
# the rule under test would otherwise reject the file that tests it.
_DEV_DOMAIN = "grph" + ".xyz"
_INT_DOMAIN = "louie" + ".internal"


@pytest.mark.parametrize(
    ("name", "body"),
    [
        ("url.py", f'u = "https://louie-dev.{_DEV_DOMAIN}"'),
        ("unknown_subdomain.py", f'u = "https://something-new.{_DEV_DOMAIN}"'),
        ("bare.md", f"See graphistry-dev.{_DEV_DOMAIN} for the dev instance."),
        ("env", f"LOUIE_SERVER=louie-dev.{_DEV_DOMAIN}"),
        ("internal.py", f'u = "https://dev.k8s.{_INT_DOMAIN}"'),
    ],
    ids=["url", "unknown_subdomain", "markdown", "dotenv", "louie_internal"],
)
def test_rejects_internal_hostnames(tmp_path: Path, name: str, body: str) -> None:
    result = run_checker(str(write(tmp_path, name, body)))

    assert result.returncode == 1, result.stderr
    assert "internal-host" in result.stderr


@pytest.mark.parametrize(
    "body",
    [
        'u = "https://louie.example.com"',  # RFC 2606
        'u = "https://hub.graphistry.com"',  # public endpoint
        'u = "https://den.louie.ai"',  # public endpoint
        'u = "https://example.com/grph"',  # path, not a host
    ],
    ids=["example_com", "hub", "den", "path_only"],
)
def test_accepts_public_and_example_hosts(tmp_path: Path, body: str) -> None:
    assert_accepted(run_checker(str(write(tmp_path, "ok.py", body))))


def test_internal_host_respects_the_pragma(tmp_path: Path) -> None:
    body = f'u = "https://louie-dev.{_DEV_DOMAIN}"  # pragma: allowlist secret'
    assert_accepted(run_checker(str(write(tmp_path, "ok.py", body))))
