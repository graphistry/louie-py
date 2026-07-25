"""The secret gates must be tested in the *rejecting* direction.

`.github/workflows/secret-detection-test.yml` only ever asserted that
`secret-detection.sh` and `pre-commit-secret-check.sh` exit 0 on a clean tree.
A gate hardwired to exit 0 satisfies that forever — which is exactly what
happened: `detect-secrets scan --baseline <f>` is an update command that always
exits 0, so both gate modes were unreachable and a live credential passed them
for ~12 months across five green workflow runs.

These tests plant secrets and assert rejection.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).parents[2]
CHECK_NEW = REPO_ROOT / "scripts" / "ci" / "check_new_secrets.py"
GATE = REPO_ROOT / "scripts" / "ci" / "secret-detection.sh"

# 10-char id shape, matching the real key format. Assembled at runtime.
GKEY = "A1B2C3" + "D4E5"

# Fake digest for baseline fixtures; a constant so the formatter cannot move a
# same-line pragma off it.
DIGEST = "abc" + "123"


def _baseline(*entries: tuple[str, str]) -> dict:
    """Baseline from `(path, hashed_secret)` pairs — matching is per-path."""
    results: dict[str, list[dict]] = {}
    for path, digest in entries:
        results.setdefault(path, []).append(
            {"type": "Secret Keyword", "hashed_secret": digest, "line_number": 1}
        )
    return {"version": "1.5.0", "results": results}


def _scan(*entries: tuple[str, int, str, str]) -> dict:
    results: dict[str, list[dict]] = {}
    for path, line, kind, digest in entries:
        results.setdefault(path, []).append(
            {"type": kind, "hashed_secret": digest, "line_number": line}
        )
    return {"version": "1.5.0", "results": results}


def run_check_new(scan: dict, baseline: dict, tmp_path: Path):
    scan_path = tmp_path / "scan.json"
    base_path = tmp_path / "base.json"
    scan_path.write_text(json.dumps(scan), encoding="utf-8")
    base_path.write_text(json.dumps(baseline), encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(CHECK_NEW),
            "--baseline",
            str(base_path),
            "--scan",
            str(scan_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


# --- check_new_secrets: the comparison the shell was only assuming ----------


def test_rejects_finding_absent_from_baseline(tmp_path: Path) -> None:
    result = run_check_new(
        _scan(("app/config.py", 12, "Secret Keyword", "deadbeef")),
        _baseline(),
        tmp_path,
    )

    assert result.returncode == 1
    assert "app/config.py:12" in result.stderr
    assert "Secret Keyword" in result.stderr


def test_accepts_finding_already_baselined(tmp_path: Path) -> None:
    result = run_check_new(
        _scan(("app/config.py", 12, "Secret Keyword", "deadbeef")),
        _baseline(("app/config.py", "deadbeef")),
        tmp_path,
    )

    assert result.returncode == 0, result.stderr


def test_accepts_empty_scan_results(tmp_path: Path) -> None:
    assert run_check_new(_scan(), _baseline(), tmp_path).returncode == 0


def test_reports_every_new_finding(tmp_path: Path) -> None:
    result = run_check_new(
        _scan(
            ("a.py", 1, "Secret Keyword", "aaa"),
            ("b.py", 2, "AWS Access Key", "bbb"),
            ("b.py", 3, "Secret Keyword", "ccc"),
        ),
        _baseline(("a.py", "aaa")),
        tmp_path,
    )

    assert result.returncode == 1
    assert "b.py:2" in result.stderr and "b.py:3" in result.stderr
    assert "a.py" not in result.stderr  # baselined
    assert "2 finding(s)" in result.stderr


def test_baseline_is_keyed_by_path_not_hash_alone(tmp_path: Path) -> None:
    """A value allowlisted in one file must not be accepted in another.

    Hash-only matching would let a demo password baselined in `docs/` pass
    silently once copied into `src/louieai/_client.py` — the exact file where
    this repo's credential incident happened.
    """
    baseline = {
        "version": "1.5.0",
        "results": {
            "docs/example.md": [
                {"type": "Secret Keyword", "hashed_secret": DIGEST, "line_number": 1}
            ]
        },
    }
    scan = _scan(("src/louieai/_client.py", 9, "Secret Keyword", "abc123"))

    result = run_check_new(scan, baseline, tmp_path)

    assert result.returncode == 1
    assert "src/louieai/_client.py:9" in result.stderr


def test_baseline_still_accepts_the_same_path(tmp_path: Path) -> None:
    baseline = {
        "version": "1.5.0",
        "results": {
            "docs/example.md": [
                {"type": "Secret Keyword", "hashed_secret": DIGEST, "line_number": 1}
            ]
        },
    }
    scan = _scan(("docs/example.md", 1, "Secret Keyword", "abc123"))

    assert run_check_new(scan, baseline, tmp_path).returncode == 0


def test_concatenated_scans_are_merged(tmp_path: Path) -> None:
    """`xargs` splits on ARG_MAX, emitting several JSON documents on one stream.

    A single `json.loads` raised `Extra data: line N`, which surfaced as
    "New secrets detected!" on a tree with no secrets — fail-closed, but
    blaming the developer for the wrong thing.
    """
    scan_path = tmp_path / "scan.json"
    base_path = tmp_path / "base.json"
    scan_path.write_text(
        json.dumps(_scan(("a.py", 1, "Secret Keyword", "aaa")))
        + "\n"
        + json.dumps(_scan(("b.py", 2, "Secret Keyword", "bbb"))),
        encoding="utf-8",
    )
    base_path.write_text(json.dumps(_baseline()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(CHECK_NEW),
            "--baseline",
            str(base_path),
            "--scan",
            str(scan_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "a.py:1" in result.stderr and "b.py:2" in result.stderr


def test_scan_without_results_key_is_an_error(tmp_path: Path) -> None:
    """Valid JSON that is not a scan must not read as 'no findings'."""
    scan_path = tmp_path / "scan.json"
    base_path = tmp_path / "base.json"
    scan_path.write_text('{"version": "1.5.0"}', encoding="utf-8")
    base_path.write_text(json.dumps(_baseline()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(CHECK_NEW),
            "--baseline",
            str(base_path),
            "--scan",
            str(scan_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "results" in result.stderr


@pytest.mark.parametrize("baseline_body", ["", "{not json", '{"results": '])
def test_unreadable_baseline_fails_closed(tmp_path: Path, baseline_body: str) -> None:
    """A truncated baseline must not be treated as 'nothing is accepted... fine'."""
    scan_path = tmp_path / "scan.json"
    base_path = tmp_path / "base.json"
    scan_path.write_text(json.dumps(_scan()), encoding="utf-8")
    base_path.write_text(baseline_body, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(CHECK_NEW),
            "--baseline",
            str(base_path),
            "--scan",
            str(scan_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "baseline" in result.stderr


def test_missing_baseline_file_fails_closed(tmp_path: Path) -> None:
    scan_path = tmp_path / "scan.json"
    scan_path.write_text(json.dumps(_scan()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(CHECK_NEW),
            "--baseline",
            str(tmp_path / "nope.json"),
            "--scan",
            str(scan_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1


def test_credential_gate_exclude_files_flag(tmp_path: Path) -> None:
    """The documented escape for files that cannot carry a pragma."""
    candidate = tmp_path / "data.csv"
    candidate.write_text(f"code,{GKEY},ok\n", encoding="utf-8")
    checker = str(REPO_ROOT / "scripts/ci/check_credential_literals.py")

    without = subprocess.run(
        [sys.executable, checker, str(candidate)],
        capture_output=True,
        text=True,
        check=False,
    )
    with_flag = subprocess.run(
        [sys.executable, checker, "--exclude-files", r"\.csv$", str(candidate)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert without.returncode == 1
    assert with_flag.returncode == 0, with_flag.stderr


def test_empty_scan_output_is_an_error_not_a_pass(tmp_path: Path) -> None:
    """A failed scan produces no output; treating that as 'clean' is how the
    old pre-commit branch silently skipped its check."""
    scan_path = tmp_path / "scan.json"
    base_path = tmp_path / "base.json"
    scan_path.write_text("", encoding="utf-8")
    base_path.write_text(json.dumps(_baseline()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(CHECK_NEW),
            "--baseline",
            str(base_path),
            "--scan",
            str(scan_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "did not run" in result.stderr


# --- end-to-end: the gate script itself must fail on a planted secret -------


@pytest.fixture
def gate_repo(tmp_path: Path) -> Path:
    """A minimal repo wired with the real gate scripts."""
    if shutil.which("detect-secrets") is None:
        # A silent skip would let the end-to-end gate tests vanish in CI, which
        # is the same "green but unverified" failure this file exists to stop.
        if os.environ.get("CI"):
            pytest.fail("detect-secrets must be on PATH in CI")
        pytest.skip("detect-secrets not on PATH")

    repo = tmp_path / "repo"
    (repo / "scripts" / "ci").mkdir(parents=True)
    for name in ("check_new_secrets.py", "check_credential_literals.py"):
        shutil.copy(REPO_ROOT / "scripts" / "ci" / name, repo / "scripts" / "ci" / name)
    shutil.copy(GATE, repo / "scripts" / "ci" / "secret-detection.sh")
    (repo / "scripts" / "ci" / "secret-detection.sh").chmod(0o755)
    (repo / "pyproject.toml").touch()
    shutil.copy(REPO_ROOT / ".secrets.baseline", repo / ".secrets.baseline")

    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "t@example.com"],
        ["git", "config", "user.name", "t"],
    ):
        subprocess.run(command, cwd=repo, check=True, capture_output=True)
    return repo


def run_gate(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["./scripts/ci/secret-detection.sh", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def test_ci_gate_rejects_planted_secret(gate_repo: Path) -> None:
    """Before the fix this printed '✅ Secret detection passed' and exited 0."""
    (gate_repo / "leak.py").write_text(
        'api_key = "zQ3RtP8xL2mN7vB4kW9jH6dF1sA5gY0c"\n',  # pragma: allowlist secret
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)

    assert run_gate(gate_repo).returncode == 1


def test_precommit_gate_rejects_staged_secret(gate_repo: Path) -> None:
    """Before the fix this printed '✅ No secrets detected' and exited 0."""
    (gate_repo / "leak.py").write_text(
        'password = "Tr0ub4dor&3-notabaseline"\n',  # pragma: allowlist secret
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)

    assert run_gate(gate_repo, "--check-only").returncode == 1


# The Graphistry gate is a separate script invoked *by* secret-detection.sh.
# Testing it directly leaves the wiring untested: removing its invocation, or
# dropping `--staged` from the pre-commit branch, both left the suite fully
# green. These exercise it through the shell entry point.


def test_gate_rejects_graphistry_literal_through_the_shell(gate_repo: Path) -> None:
    """Kills the mutant where the credential-gate call is removed from the shell."""
    (gate_repo / "conf.py").write_text(f'k = "{GKEY}"\n', encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)

    assert run_gate(gate_repo).returncode == 1
    assert run_gate(gate_repo, "--check-only").returncode == 1


def test_precommit_gate_uses_the_index_for_graphistry_literals(gate_repo: Path) -> None:
    """Kills the mutant where `--staged` is dropped from the pre-commit branch.

    Stage the credential, then clean the worktree: only an index-aware scan
    still sees it.
    """
    target = gate_repo / "conf.py"
    target.write_text(f'k = "{GKEY}"\n', encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)
    target.write_text('k = "<your-personal-key-id>"\n', encoding="utf-8")

    assert run_gate(gate_repo, "--check-only").returncode == 1


def test_gate_rejects_rename_plus_edit(gate_repo: Path) -> None:
    """`git mv` + edit reports `R`, which --diff-filter=ACM drops."""
    original = gate_repo / "big.py"
    original.write_text("x = 1\n" * 40, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-qm", "seed"], cwd=gate_repo, check=True, capture_output=True
    )

    subprocess.run(["git", "mv", "big.py", "cfg.py"], cwd=gate_repo, check=True)
    renamed = gate_repo / "cfg.py"
    # Assembled at runtime so this file carries no scannable literal of its own.
    planted = (
        "aws_secret_access_key" + ' = "' + "wJalrXUtnFEMI" + "K7MDENGbPxRfi" + '"\n'
    )
    renamed.write_text(renamed.read_text(encoding="utf-8") + planted, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)

    assert run_gate(gate_repo, "--check-only").returncode == 1


def test_gate_handles_filenames_with_spaces(gate_repo: Path) -> None:
    """`xargs` word-splitting made a spaced filename scan nothing and pass."""
    (gate_repo / "zz spaced.py").write_text(
        'password = "Tr0ub4dor&3-notabaseline"\n',  # pragma: allowlist secret
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)

    assert run_gate(gate_repo, "--check-only").returncode == 1


def test_missing_baseline_does_not_silently_pass(gate_repo: Path) -> None:
    """Generating a baseline accepts everything, so that run must not succeed."""
    (gate_repo / "leak.py").write_text(
        'api_key = "zQ3RtP8xL2mN7vB4kW9jH6dF1sA5gY0c"\n',  # pragma: allowlist secret
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)
    (gate_repo / ".secrets.baseline").unlink()

    assert run_gate(gate_repo).returncode == 1


# The remediation guidance must be discoverable at the moment of failure, not
# only in a doc nobody reads. These pin that the failure output actually teaches
# the fix, and that the doc it points at exists and covers it.

DOC = REPO_ROOT / ".secret-patterns.md"
FIXTURE_SECTION = "Writing tests that contain deliberate fake secrets"


def test_credential_gate_failure_explains_how_to_fix(tmp_path: Path) -> None:
    candidate = tmp_path / "f.py"
    candidate.write_text(f'k = "{GKEY}"\n', encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/ci/check_credential_literals.py"),
            str(candidate),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "pragma: allowlist secret" in result.stderr
    assert "SAME line" in result.stderr  # the mistake that silently does nothing
    assert "at runtime" in result.stderr  # the preferred fixture technique
    assert "--exclude-files" in result.stderr
    assert ".secret-patterns.md" in result.stderr


def test_new_secret_failure_explains_how_to_fix(tmp_path: Path) -> None:
    result = run_check_new(
        _scan(("app/config.py", 12, "Secret Keyword", "deadbeef")),
        _baseline(),
        tmp_path,
    )

    assert result.returncode == 1
    assert "pragma: allowlist secret" in result.stderr
    assert "at runtime" in result.stderr
    assert "ANYWHERE in the tree" in result.stderr  # why baselining is the last resort
    assert ".secret-patterns.md" in result.stderr


def test_documented_guidance_exists_and_covers_all_three_routes() -> None:
    """The error messages point here; the section must actually be present."""
    doc = DOC.read_text(encoding="utf-8")

    assert FIXTURE_SECTION in doc
    section = doc.split(FIXTURE_SECTION, 1)[1]
    for expected in ("at runtime", "same line", "--exclude-files", "Never re-baseline"):
        assert expected.lower() in section.lower(), expected


def test_gate_scans_the_last_staged_file(gate_repo: Path) -> None:
    """The staged list is NUL-*terminated*, not NUL-separated.

    `read -r -d ''` only emits a field when it sees the delimiter, so joining
    paths with NUL instead of terminating each one silently dropped whichever
    file sorted last — it was never scanned at all.
    """
    # 'zzz_' sorts after every other file the fixture stages.
    (gate_repo / "zzz_last.py").write_text(
        'password = "Tr0ub4dor&3-notabaseline"\n',  # pragma: allowlist secret
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)

    assert run_gate(gate_repo, "--check-only").returncode == 1


def test_gate_passes_on_clean_tree(gate_repo: Path) -> None:
    (gate_repo / "ok.py").write_text('password = "<your-password>"\n', encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=gate_repo, check=True, capture_output=True)

    assert run_gate(gate_repo).returncode == 0
    assert run_gate(gate_repo, "--check-only").returncode == 0
