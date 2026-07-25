#!/usr/bin/env python3
"""Fail when a detect-secrets scan finds anything not already in the baseline.

`scripts/ci/secret-detection.sh` used to gate on the exit code of

    detect-secrets scan --baseline .secrets.baseline

That command is an *update* operation, not an assertion: it rewrites the baseline
file in place, writes nothing to stdout, and **exits 0 no matter what it finds**.
Both the CI and pre-commit gates branched on `|| print_error`, so neither branch
was reachable and a known-live credential passed both. This module supplies the
comparison the shell was assuming.

Reads a scan JSON (stdin or a path) and compares its findings against the
baseline by `hashed_secret`. Reports `path:line:type` only — never a value.

Exit 1 when a finding is not in the baseline.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

Finding = tuple[str, int, str]


def _load(source: str | None) -> dict[str, Any]:
    """Parse one *or more* concatenated scan objects and union their results.

    `xargs` splits on ARG_MAX, so a large commit produces several
    back-to-back JSON documents on one stream. A single `json.loads` then fails
    with `Extra data: line N`, which surfaced as "New secrets detected!" on a
    tree with no secrets — fail-closed, but blaming the developer for the wrong
    thing.
    """
    text = Path(source).read_text(encoding="utf-8") if source else sys.stdin.read()
    if not text.strip():
        # An empty scan is not "clean" — it usually means the scan itself failed
        # (wrong cwd, bad args). Treat it as an error rather than a pass.
        raise ValueError("empty scan output; the detect-secrets scan did not run")

    decoder = json.JSONDecoder()
    merged: dict[str, Any] = {"results": {}}
    index = 0
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        document, index = decoder.raw_decode(text, index)
        if not isinstance(document, dict) or "results" not in document:
            # detect-secrets always emits a `results` key. Its absence means we
            # are not looking at a scan, and treating that as "no findings"
            # would be another silent pass.
            raise ValueError(
                "scan output has no 'results' key; not a detect-secrets scan"
            )
        for path, entries in document["results"].items():
            merged["results"].setdefault(path, []).extend(entries)
    return merged


def baseline_hashes(baseline: dict[str, Any]) -> set[tuple[str, str]]:
    """Accepted findings, keyed by `(path, hashed_secret)`.

    Keying on the hash alone would accept a value *anywhere* once it is
    baselined in one place — so a demo password allowlisted in `docs/` would
    pass silently if copied into `src/louieai/_client.py`, which is exactly
    where this repo's incident happened. detect-secrets' own baseline semantics
    are per-file; match them.
    """
    return {
        (path, entry["hashed_secret"])
        for path, entries in baseline.get("results", {}).items()
        for entry in entries
        if "hashed_secret" in entry
    }


def new_findings(scan: dict[str, Any], known: set[tuple[str, str]]) -> list[Finding]:
    """Findings in `scan` not already accepted for that same path."""
    found: list[Finding] = []
    for path, entries in sorted(scan.get("results", {}).items()):
        for entry in entries:
            if (path, entry.get("hashed_secret")) in known:
                continue
            found.append(
                (path, int(entry.get("line_number", 0)), str(entry.get("type", "?")))
            )
    return found


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=".secrets.baseline")
    parser.add_argument("--scan", default=None, help="scan JSON path (default: stdin)")
    args = parser.parse_args(argv)

    try:
        scan = _load(args.scan)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: could not read detect-secrets scan: {exc}", file=sys.stderr)
        return 1

    try:
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: could not read baseline {args.baseline}: {exc}", file=sys.stderr)
        return 1

    findings = new_findings(scan, baseline_hashes(baseline))
    if not findings:
        return 0

    for path, line, kind in findings:
        print(f"{path}:{line}: new secret detected [{kind}]", file=sys.stderr)
    print(
        f"\n{len(findings)} finding(s) not in {args.baseline}. Values are not "
        "printed.\n"
        "  Real credential      -> remove it and use an environment variable.\n"
        "  Deliberate test fixture -> build it at runtime so no literal exists, or "
        "append '# pragma: allowlist secret' on the SAME line.\n"
        "  Genuine false positive -> re-baseline with "
        f"`detect-secrets scan > {args.baseline}` and review the diff. Note a "
        "baseline entry accepts that value ANYWHERE in the tree, so prefer a "
        "pragma for a one-off.\n"
        "See .secret-patterns.md, 'Writing tests that contain deliberate fake "
        "secrets'.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
