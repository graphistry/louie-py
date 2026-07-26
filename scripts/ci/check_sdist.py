#!/usr/bin/env python3
"""Screen a built sdist/wheel before it can be published.

`plan.md`, `weekly_report.md`, `tests/`, and `.env.example` shipped in every
release through 0.9.0. `MANIFEST.in` now excludes them, and a unit test asserts
those rules exist — but a rule is not an artifact. Packaging behaviour depends on
setuptools defaults, the build backend, and which files happen to be tracked, so
the only reliable check is to open the archive that is about to be uploaded.

`tests/unit/security/test_release_artifact_gates.py` proves this rejects — it
plants each leak type into each artifact type and asserts a non-zero exit.

Two categories of check:

`paths`
    Reject internal working material — top-level notes, the test tree, scratch
    directories, and the checked-in virtualenv.

`credentials`
    Run the deterministic Graphistry key / internal-host gate over every text
    member, **and** a `detect-secrets` sweep compared against `.secrets.baseline`
    so the generic classes (AWS keys, private keys, high-entropy strings,
    keyword-adjacent values) are covered too. This repo published live
    credentials inside `plan.md` and `src/louieai/_client.py` for ~12 months
    across 16 releases; PyPI uploads are immutable, so the last opportunity to
    catch that is here, before upload.

    `detect-secrets scan` enumerates files **via git**, so in an extracted
    archive — which is not a repository — it silently reports nothing. `scan
    --all-files` is mandatory here; without it the sweep looks clean on an
    archive containing anything at all.

Exit 1 on any finding.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from collections.abc import Sequence
from pathlib import Path

# Paths that must never appear in a distribution, relative to the archive root.
FORBIDDEN = (
    re.compile(r"^plan\.md$"),
    re.compile(r"^weekly_report\.md$"),
    re.compile(r"^tests/"),
    re.compile(r"^plans/"),
    re.compile(r"^templates/"),
    re.compile(r"^test-env-[^/]*/"),
    re.compile(r"^\.env(\.|$)"),
    re.compile(r"^\.secrets\.baseline$"),
)

_TEXT_SUFFIXES = {".py", ".md", ".txt", ".toml", ".cfg", ".yml", ".yaml", ".ipynb"}


def _members(archive: Path) -> list[str]:
    """Archive member paths, with the top-level version directory stripped."""
    if archive.suffix == ".whl" or archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            return zf.namelist()
    with tarfile.open(archive) as tf:
        # sdists nest everything under `<name>-<version>/`.
        return [n.split("/", 1)[1] for n in tf.getnames() if "/" in n]


def _extract(archive: Path, destination: Path) -> None:
    if archive.suffix == ".whl" or archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(destination)
        return
    with tarfile.open(archive) as tf:
        # Our own build output, but `filter="data"` is free and silences the
        # 3.14 deprecation. The kwarg landed in 3.11.4 / 3.12; on 3.10 the
        # permissive default is all that is available.
        if sys.version_info >= (3, 12):
            tf.extractall(destination, filter="data")
        else:
            tf.extractall(destination)


def check_paths(archive: Path) -> list[str]:
    """Forbidden members, if any."""
    return sorted(
        name
        for name in _members(archive)
        if name and any(pattern.search(name) for pattern in FORBIDDEN)
    )


# Archive member paths -> the repository path the content came from, so a
# finding can be compared against `.secrets.baseline` on its original key.
# Without this every artifact finding looks new: a wheel ships `louieai/` where
# the repo has `src/louieai/`, and PKG-INFO / METADATA are generated files whose
# body is `README.md`.
_PATH_REWRITES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^louieai/"), "src/louieai/"),
    (re.compile(r"^PKG-INFO$"), "README.md"),
    (re.compile(r"^src/[^/]+\.egg-info/PKG-INFO$"), "README.md"),
    (re.compile(r"^[^/]+\.dist-info/METADATA$"), "README.md"),
)


def normalize_scan_paths(scan_json: str) -> str:
    """Rewrite archive-relative result keys to their repository equivalents.

    Only known generated/relocated paths are rewritten. Anything unrecognised is
    left alone, so an unexpected file fails closed against the baseline rather
    than being quietly mapped onto some allowlisted path.
    """
    document = json.loads(scan_json)
    rewritten: dict[str, list[dict[str, object]]] = {}
    for path, entries in document.get("results", {}).items():
        target = path
        for pattern, replacement in _PATH_REWRITES:
            if pattern.search(path):
                target = pattern.sub(replacement, path)
                break
        rewritten.setdefault(target, []).extend(entries)
    document["results"] = rewritten
    return json.dumps(document)


def _archive_root_after_extract(archive: Path, destination: Path) -> Path:
    """Extract `archive` into `destination` and return its content root."""
    _extract(archive, destination)
    return _archive_root(destination)


def _archive_root(extracted: Path) -> Path:
    """sdists nest under `<name>-<version>/`; wheels extract flat."""
    entries = [p for p in extracted.iterdir() if p.is_dir()]
    if len(entries) == 1 and not (extracted / "louieai").exists():
        return entries[0]
    return extracted


def check_credentials(archive: Path, checker: Path) -> str:
    """Deterministic Graphistry/internal-host gate. Empty string when clean."""
    with tempfile.TemporaryDirectory() as tmp:
        root = _archive_root_after_extract(archive, Path(tmp))
        # Run from the archive root with relative paths, so a finding reads
        # `src/louieai/_client.py:265` rather than a `/tmp/tmpXXXX/...` path
        # that says nothing about which shipped file to fix.
        targets = sorted(
            str(path.relative_to(root))
            for path in root.rglob("*")
            if path.is_file() and path.suffix in _TEXT_SUFFIXES
        )
        if not targets:
            return ""
        result = subprocess.run(
            [sys.executable, str(checker), *targets],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        return "" if result.returncode == 0 else result.stderr


def check_generic_secrets(archive: Path, baseline: Path, comparer: Path) -> str:
    """detect-secrets sweep vs the baseline. Empty string when clean.

    Covers the classes the deterministic gate does not: AWS keys, private keys,
    high-entropy strings, keyword-adjacent values.
    """
    if not baseline.is_file() or not comparer.is_file():
        return ""
    if shutil.which("detect-secrets") is None:
        return "detect-secrets not found; cannot sweep the archive\n"

    with tempfile.TemporaryDirectory() as tmp:
        scan_root = _archive_root_after_extract(archive, Path(tmp))
        # --all-files is required: detect-secrets enumerates via git, and an
        # extracted archive is not a repository, so a bare scan finds nothing.
        scan = subprocess.run(
            ["detect-secrets", "scan", "--all-files"],
            cwd=scan_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if scan.returncode != 0 or not scan.stdout.strip():
            return f"detect-secrets scan failed: {scan.stderr[:300]}\n"
        compared = subprocess.run(
            [sys.executable, str(comparer), "--baseline", str(baseline)],
            input=normalize_scan_paths(scan.stdout),
            capture_output=True,
            text=True,
            check=False,
        )
        return "" if compared.returncode == 0 else compared.stderr


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", help="built .tar.gz / .whl files")
    parser.add_argument(
        "--credential-checker",
        default=str(Path(__file__).with_name("check_credential_literals.py")),
    )
    parser.add_argument(
        "--baseline",
        default=str(Path(__file__).resolve().parents[2] / ".secrets.baseline"),
    )
    args = parser.parse_args(argv)

    checker = Path(args.credential_checker)
    failed = False

    for name in args.archives:
        archive = Path(name)
        if not archive.is_file():
            print(f"error: no such archive: {archive}", file=sys.stderr)
            return 1

        forbidden = check_paths(archive)
        if forbidden:
            failed = True
            print(f"{archive.name}: internal material must not ship:", file=sys.stderr)
            for entry in forbidden[:20]:
                print(f"  {entry}", file=sys.stderr)
            if len(forbidden) > 20:
                print(f"  ... and {len(forbidden) - 20} more", file=sys.stderr)
            print("  Fix by excluding it in MANIFEST.in.", file=sys.stderr)

        report = check_credentials(archive, checker) if checker.is_file() else ""
        if report:
            failed = True
            print(f"{archive.name}: credential-shaped content:", file=sys.stderr)
            print(report, file=sys.stderr)

        generic = check_generic_secrets(
            archive,
            Path(args.baseline),
            Path(__file__).with_name("check_new_secrets.py"),
        )
        if generic:
            failed = True
            print(f"{archive.name}: detect-secrets findings:", file=sys.stderr)
            print(generic, file=sys.stderr)

        if not forbidden and not report and not generic:
            print(f"{archive.name}: clean")

    if failed:
        print(
            "\nA published artifact cannot be recalled — PyPI uploads are "
            "immutable and yanking does not delete files. Fix before releasing.",
            file=sys.stderr,
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
