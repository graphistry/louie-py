#!/usr/bin/env python3
"""Screen a built sdist/wheel before it can be published.

`plan.md`, `weekly_report.md`, `tests/`, and `.env.example` shipped in every
release through 0.9.0. `MANIFEST.in` now excludes them, and a unit test asserts
those rules exist — but a rule is not an artifact. Packaging behaviour depends on
setuptools defaults, the build backend, and which files happen to be tracked, so
the only reliable check is to open the archive that is about to be uploaded.

Two independent checks:

`paths`
    Reject internal working material — top-level notes, the test tree, scratch
    directories, and the checked-in virtualenv.

`credentials`
    Run the deterministic credential gate over every text member. This repo
    published live credentials inside `plan.md` and `src/louieai/_client.py` for
    ~12 months across 16 releases; PyPI uploads are immutable, so the last
    opportunity to catch that is here, before upload.

Exit 1 on any finding.
"""

from __future__ import annotations

import argparse
import re
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
        # Extracting our own build output, not untrusted input.
        tf.extractall(destination)


def check_paths(archive: Path) -> list[str]:
    """Forbidden members, if any."""
    return sorted(
        name
        for name in _members(archive)
        if name and any(pattern.search(name) for pattern in FORBIDDEN)
    )


def check_credentials(archive: Path, checker: Path) -> str:
    """Empty string when clean, otherwise the gate's report."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _extract(archive, root)
        targets = [
            str(path)
            for path in root.rglob("*")
            if path.is_file() and path.suffix in _TEXT_SUFFIXES
        ]
        if not targets:
            return ""
        result = subprocess.run(
            [sys.executable, str(checker), *targets],
            capture_output=True,
            text=True,
            check=False,
        )
        return "" if result.returncode == 0 else result.stderr


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", help="built .tar.gz / .whl files")
    parser.add_argument(
        "--credential-checker",
        default=str(Path(__file__).with_name("check_credential_literals.py")),
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

        if not forbidden and not report:
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
