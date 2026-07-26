"""Every leak type is rejected in every release artifact type.

`MANIFEST.in` rules and a passing `check_sdist.py` run are not evidence. This
repo shipped `plan.md` — containing live credentials — in sixteen consecutive
releases while a secret gate reported success on every one of them, because the
gate's failure branch was unreachable. A gate is only trustworthy if something
proves it *rejects*.

So this module builds real archives with a real leak planted in each, and
asserts the screen fails. Coverage is a matrix:

    leak type          x   artifact type
    ---------------        -------------
    Graphistry key id      sdist (.tar.gz)
    Graphistry key secret  wheel (.whl)
    internal hostname
    AWS access key
    private key block
    keyword-adjacent value
    high-entropy string
    internal notes path
    test-tree path

Three controls keep the matrix honest:

* a clean archive of each type must PASS — otherwise "everything fails" would
  look identical to "everything is caught";
* each leak is attributed to the specific gate that catches it, so a gate that
  quietly stops working cannot hide behind a different one;
* `test_bare_scan_finds_nothing_in_an_extracted_archive` pins the specific
  defect that would make the sweep hollow again.

Planted values are assembled at runtime so no literal exists in this file for
the repository's own scanners to flag. That is the same technique an attacker
would use to evade a literal scanner, which is exactly why the archive contents
— not the source of this test — are what gets scanned.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tarfile
import zipfile
from collections.abc import Iterable
from pathlib import Path

import pytest

from tests.utils import repo_root

SCREEN = repo_root() / "scripts" / "ci" / "check_sdist.py"
BASELINE = repo_root() / ".secrets.baseline"

# --- planted leaks -----------------------------------------------------------
# Each value is concatenated at import time; see the module docstring.

# Named for their shape, not their role: `_KEY_ID = "..."` reads to
# detect-secrets' KeywordDetector as a keyword/value pair and trips the
# repository's own gate on this file.
_SHAPE_10 = "K3PQ" + "7RTX2M"  # Graphistry personal key id
_SHAPE_16 = "QF7M" + "XB2N" + "9WHR" + "4KTD"  # Graphistry personal key secret
_HOST = "louie-canary." + "grph" + ".xyz"
_AWS = "AKIA" + "IOSFODNN7" + "EXAMPLE"
# Entropy must clear detect-secrets' 4.5 bit threshold; a readable base64
# string ("supersecretvalue...") measures 4.49 and slips through.
_ENTROPY = "aG7Kd2XpQvBs" + "4TnZmR8yLcWj" + "E1uYfNb3OxAi" + "6VtQrPzMh5Dg"
_PRIVATE_KEY = (
    "-----BEGIN RSA PRIVATE"
    + " KEY-----\n"
    + _ENTROPY
    + "\n-----END RSA PRIVATE KEY-----"
)

# gate: which check is expected to catch it.
#   "literals" -> scripts/ci/check_credential_literals.py
#   "sweep"    -> detect-secrets, compared against .secrets.baseline
#   "paths"    -> the forbidden-path list
LEAKS: tuple[tuple[str, str, str, str], ...] = (
    (
        "graphistry-key-id",
        "literals",
        "src/louieai/leak.py",
        f'KEY_ID = "{_SHAPE_10}"\n',
    ),
    (
        "graphistry-key-secret",
        "literals",
        "src/louieai/leak.py",
        f'KEY_SECRET = "{_SHAPE_16}"\n',
    ),
    (
        "internal-hostname",
        "literals",
        "src/louieai/leak.py",
        f'SERVER = "https://{_HOST}"\n',
    ),
    ("aws-access-key", "sweep", "src/louieai/leak.py", f'AWS_ID = "{_AWS}"\n'),
    ("private-key", "sweep", "src/louieai/leak.pem", _PRIVATE_KEY + "\n"),
    (
        "keyword-adjacent",
        "sweep",
        "src/louieai/leak.py",
        f'api_key = "{_ENTROPY}"\n',
    ),
    (
        "high-entropy",
        "sweep",
        "src/louieai/leak.py",
        f'TOKEN = "{_ENTROPY}"\n',
    ),
    ("internal-notes-path", "paths", "plan.md", "# internal notes\n"),
    ("test-tree-path", "paths", "tests/test_leak.py", "def test_x():\n    pass\n"),
)

ARTIFACTS = ("sdist", "wheel")

_DIST = "louieai-9.9.9"


def _clean_tree() -> dict[str, str]:
    """A minimal, credential-free package layout."""
    return {
        "README.md": "# louieai\n\nA client library.\n",
        "pyproject.toml": '[project]\nname = "louieai"\n',
        "src/louieai/__init__.py": '"""louieai."""\n\n__version__ = "9.9.9"\n',
    }


def _wheel_tree(files: dict[str, str]) -> dict[str, str]:
    """Re-map an sdist-shaped tree onto wheel layout.

    A wheel ships `louieai/` where the sdist ships `src/louieai/`, and carries
    `.dist-info/METADATA` in place of `PKG-INFO`. The screen has to handle both,
    so the matrix runs the identical leak through each shape.
    """
    mapped: dict[str, str] = {}
    for name, body in files.items():
        if name.startswith("src/louieai/"):
            mapped[name[len("src/") :]] = body
        elif name in {"README.md", "pyproject.toml"}:
            continue
        else:
            mapped[name] = body
    mapped[f"{_DIST}.dist-info/METADATA"] = "Metadata-Version: 2.1\nName: louieai\n"
    mapped[f"{_DIST}.dist-info/RECORD"] = ""
    return mapped


def build_artifact(kind: str, files: dict[str, str], destination: Path) -> Path:
    """Write a real `.tar.gz` / `.whl` containing `files`."""
    if kind == "sdist":
        archive = destination / f"{_DIST}.tar.gz"
        payload = dict(files)
        payload["PKG-INFO"] = "Metadata-Version: 2.1\nName: louieai\n"
        staging = destination / "staging" / _DIST
        for name, body in payload.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        with tarfile.open(archive, "w:gz") as tf:
            tf.add(staging, arcname=_DIST)
        return archive

    if kind == "wheel":
        archive = destination / f"{_DIST}-py3-none-any.whl"
        with zipfile.ZipFile(archive, "w") as zf:
            for name, body in _wheel_tree(files).items():
                zf.writestr(name, body)
        return archive

    raise AssertionError(f"unknown artifact kind: {kind}")


def run_screen(
    archive: Path, *, baseline: Path = BASELINE, sweep: bool = True
) -> tuple[int, str]:
    """Run the release screen. Returns (exit code, combined output)."""
    command = [sys.executable, str(SCREEN), str(archive), "--baseline", str(baseline)]
    if not sweep:
        command.append("--no-sweep")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout + result.stderr


def _planted(files: dict[str, str], path: str, body: str) -> dict[str, str]:
    merged = dict(files)
    merged[path] = merged.get(path, "") + body
    return merged


@pytest.fixture(scope="module", autouse=True)
def _require_detect_secrets() -> None:
    """Fail loudly, never skip.

    A skipped security test is indistinguishable from a passing one in CI
    output, and "the gate didn't actually run" is the failure this whole module
    exists to prevent. `detect-secrets` is a declared dev dependency.
    """
    if shutil.which("detect-secrets") is None:
        pytest.fail(
            "detect-secrets is not on PATH; the artifact sweep cannot run. "
            "Install dev dependencies (`uv sync --locked --all-extras`) rather "
            "than skipping this module."
        )


@pytest.mark.parametrize("artifact", ARTIFACTS)
@pytest.mark.parametrize(
    ("leak", "gate", "path", "body"),
    LEAKS,
    ids=[entry[0] for entry in LEAKS],
)
def test_leak_is_rejected(
    tmp_path: Path, artifact: str, leak: str, gate: str, path: str, body: str
) -> None:
    """Every leak type is rejected in every artifact type."""
    files = _planted(_clean_tree(), path, body)
    archive = build_artifact(artifact, files, tmp_path)

    code, output = run_screen(archive)

    assert code == 1, f"{leak} shipped undetected in the {artifact}:\n{output}"
    assert "clean" not in output, f"{leak} in {artifact} was reported clean:\n{output}"


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_clean_artifact_passes(tmp_path: Path, artifact: str) -> None:
    """Control: the screen is not simply failing everything.

    Without this, a screen that rejected all input would satisfy every
    rejection assertion above while blocking all releases.
    """
    archive = build_artifact(artifact, _clean_tree(), tmp_path)
    code, output = run_screen(archive)
    assert code == 0, f"clean {artifact} was rejected:\n{output}"
    assert "clean" in output


@pytest.mark.parametrize(
    ("leak", "gate", "path", "body"),
    [entry for entry in LEAKS if entry[1] == "sweep"],
    ids=[entry[0] for entry in LEAKS if entry[1] == "sweep"],
)
def test_sweep_leaks_are_attributable_to_the_sweep(
    tmp_path: Path, leak: str, gate: str, path: str, body: str
) -> None:
    """Disabling the detect-secrets sweep must let its leaks through.

    Attribution, not redundancy. If an AWS key were only ever caught by the
    literal gate's incidental shape matching, the sweep could rot away silently
    and the matrix above would stay green. `--no-sweep` turns it off; these
    leaks must then survive.
    """
    files = _planted(_clean_tree(), path, body)
    archive = build_artifact("sdist", files, tmp_path)

    code, output = run_screen(archive, sweep=False)

    assert code == 0, (
        f"{leak} was still rejected with the sweep disabled, so this row does "
        f"not prove the sweep works:\n{output}"
    )


def test_bare_scan_finds_nothing_in_an_extracted_archive(tmp_path: Path) -> None:
    """Pin the defect that would make the artifact sweep hollow.

    `detect-secrets scan` enumerates files through git. An extracted archive is
    not a repository, so a bare scan reports zero findings on an archive full of
    credentials — exit 0, valid JSON, no error. `--all-files` is what makes it
    look at anything.

    This is the same shape as the original incident (a scan command that could
    not fail), so it gets a test that fails if anyone drops the flag.
    """
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    for name, body in _planted(
        _clean_tree(), "src/louieai/leak.py", f'AWS_ID = "{_AWS}"\n'
    ).items():
        target = extracted / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")

    def count(*args: str) -> int:
        result = subprocess.run(
            ["detect-secrets", "scan", *args],
            cwd=extracted,
            capture_output=True,
            text=True,
            check=True,
        )
        results = json.loads(result.stdout).get("results", {})
        return sum(len(entries) for entries in results.values())

    assert count() == 0, (
        "A bare scan now reports findings outside a repository. If detect-secrets "
        "changed this behaviour the --all-files requirement can be revisited; "
        "until then check_sdist.py must keep passing it."
    )
    assert count("--all-files") > 0, "--all-files found nothing; the sweep is broken"


def _screen_source() -> str:
    return SCREEN.read_text(encoding="utf-8")


def test_screen_never_invokes_a_bare_scan() -> None:
    """Guard the flag itself, not just its current effect."""
    source = _screen_source()
    assert '"scan", "--all-files"' in source, (
        "check_sdist.py must invoke detect-secrets with --all-files; without it "
        "the scan silently reports nothing on an extracted archive"
    )


def _workflow_steps(path: Path) -> Iterable[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]


@pytest.mark.parametrize("workflow", ["ci.yml", "publish.yml"])
def test_every_build_is_screened(workflow: str) -> None:
    """A gate that is not wired to every build is not a gate.

    Any job that runs `python -m build` produces an artifact that could be
    uploaded or installed, so each one must be followed by the screen.
    """
    path = repo_root() / ".github" / "workflows" / workflow
    lines = _workflow_steps(path)
    builds = sum(1 for line in lines if line.startswith("run:") and "-m build" in line)
    screens = sum(1 for line in lines if "check_sdist.py" in line)
    assert builds > 0, (
        f"{workflow} builds nothing; this test is checking the wrong file"
    )
    assert screens >= builds, (
        f"{workflow} runs `python -m build` {builds}x but only screens {screens}x; "
        "every built artifact must be screened before it is published or installed"
    )


def test_a_missing_baseline_is_an_error_not_a_pass(tmp_path: Path) -> None:
    """The screen must never report success when it could not run.

    The original incident was a gate that passed because its check was
    unreachable. A sweep that silently degrades to "clean" when its baseline is
    absent is the same bug with a different trigger.
    """
    archive = build_artifact("sdist", _clean_tree(), tmp_path)
    code, output = run_screen(archive, baseline=tmp_path / "no-such-baseline.json")
    assert code == 1, f"a missing baseline was treated as clean:\n{output}"
    assert "baseline not found" in output
