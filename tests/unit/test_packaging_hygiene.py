"""Internal material must not be tracked, and must not ship in the sdist.

`plan.md` was tracked from 2025-08-02 and shipped in every sdist through 0.9.0,
along with `tests/` and `.env.example`. Nothing caught it: `.gitignore` did not
cover the root file, and setuptools' default sdist sweeps in top-level files and
the test tree unless a MANIFEST.in says otherwise.

These are cheap structural assertions, not a build — the sdist contents are
derived from MANIFEST.in rules rather than by invoking the packaging toolchain.
"""

from __future__ import annotations

import subprocess

import pytest

from tests.utils import repo_root

pytestmark = pytest.mark.unit

# Paths that are internal working material, not shippable source.
FORBIDDEN_TRACKED = (
    "plan.md",
    "weekly_report.md",
)
FORBIDDEN_PREFIXES = ("plans/",)


def _tracked() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=repo_root(), text=True)
    return [line for line in out.splitlines() if line]


def test_internal_notes_are_not_tracked() -> None:
    tracked = _tracked()

    offenders = [p for p in tracked if p in FORBIDDEN_TRACKED]
    offenders += [p for p in tracked if p.startswith(FORBIDDEN_PREFIXES)]

    assert offenders == [], (
        f"internal material is tracked and will ship: {offenders}. "
        "Add it to .gitignore and MANIFEST.in."
    )


def test_manifest_excludes_internal_material() -> None:
    """MANIFEST.in is what actually keeps these out of the sdist."""
    manifest = (repo_root() / "MANIFEST.in").read_text(encoding="utf-8")

    for rule in ("prune tests", "exclude plan.md", "prune plans"):
        assert rule in manifest, f"MANIFEST.in is missing: {rule}"


def test_gitignore_anchors_the_root_plan_file() -> None:
    """`/plan.md` must be anchored so plans/<task>/plan.md still works.

    An unanchored `plan.md` would also ignore the plan skill's per-task files,
    which are meant to be creatable.
    """
    ignore = (repo_root() / ".gitignore").read_text(encoding="utf-8")

    assert "/plan.md" in ignore
    assert "\nplan.md" not in ignore, "unanchored entry would over-match"
