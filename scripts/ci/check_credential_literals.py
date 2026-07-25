#!/usr/bin/env python3
"""Reject hard-coded Graphistry personal keys without printing their values.

`detect-secrets` entropy heuristics miss short Graphistry personal keys, so this
adds a deterministic gate. It reports only path, line, and rule name — never the
matched value — so CI logs cannot leak what the check is protecting.

Deliberately stdlib-only: it must run inside a pre-commit hook before project
dependencies (or a virtualenv) necessarily exist, which is why it is invoked as
`python3` rather than `uv run` despite `ai/README.md`'s general guidance.

Two independent rules run over every tracked text file:

`value-shape`
    A standalone token matching the Graphistry personal-key shape, matched
    *without* requiring surrounding quotes. Quoting is not a reliable signal:
    the same value appears unquoted in `.env` and shell exports, backslash-quoted
    inside `.ipynb` JSON, and bare in YAML and Markdown. Matching the token
    itself covers all of them. Requiring a letter/digit mix keeps ordinary
    all-caps words (`"PRODUCTION"`, `"LINESTRING"`) from tripping the gate.

`key-context`
    A value assigned to a `personal_key_id` / `personal_key_secret` identifier
    that does not match the known shape but is not an obvious placeholder. This
    is the forward-compatibility net for a future key format, so it accepts
    `GRAPHISTRY_`-prefixed names and `=`, `:`, and `,` separators.

`internal-host`
    An internal hostname. Test fixtures and docs should use RFC 2606 example
    domains or the public endpoints, not real infrastructure names.

    Only *generalizable* patterns live here. A public repository cannot carry a
    denylist of the specific account or organisation names it is trying to keep
    out, because the denylist publishes them; those belong in a local
    `.git/hooks/pre-commit` (or a gitignored pattern file), not in tracked
    source. A domain regex reveals nothing beyond public DNS and covers every
    subdomain, including ones nobody has thought of yet.

Suppress a genuine false positive with a trailing `# pragma: allowlist secret`
(the same marker `detect-secrets` uses).

Exit 1 on any finding.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

# Observed Graphistry personal-key shapes: uppercase alphanumeric, fixed widths.
_SHAPES: dict[str, int] = {"personal_key_id": 10, "personal_key_secret": 16}
_SHAPE_WIDTHS = sorted(set(_SHAPES.values()))
_VALUE_SHAPE = re.compile(
    # `+` and `/` are base64-interior characters and `=` is base64 padding, so a
    # random 10/16-char uppercase run inside an embedded image blob would
    # otherwise match — measured ~1 per 400 KB, and an `.ipynb` data URI has no
    # place to put a `# pragma` escape. Excluding `+/` on both sides and `=` on
    # the right removes every such hit (0 across 4 MB of random base64) while
    # still matching `KEY=VALUE` in `.env`, where `=` *precedes* the token.
    "(?<![A-Za-z0-9+/])("
    + "|".join(rf"[A-Z0-9]{{{width}}}" for width in _SHAPE_WIDTHS)
    + ")(?![A-Za-z0-9+/=])"
)

# No leading \b: it never fires after an underscore, which would miss
# GRAPHISTRY_PERSONAL_KEY_SECRET — the exact name DEVELOP.md tells developers to
# use. `:` is in the separator class so dict, JSON, and YAML entries match too.
_KEY_CONTEXT = re.compile(
    r"""
    (?P<key>personal_key_(?:id|secret))\b
    ["']?
    [ \t]* (?: : [^=:,\r\n]{0,40} )? [ \t]*
    (?: = | : | , )
    [ \t]*
    (?P<quote>["'])
    (?P<value>[^"'\r\n]*)
    (?P=quote)
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Internal infrastructure domains. Deliberately a domain-level pattern, not a
# list of known hosts: the local hook enumerated two specific ones, so any new
# subdomain passed silently.
_INTERNAL_HOSTS = re.compile(
    r"(?<![A-Za-z0-9.-])[A-Za-z0-9][A-Za-z0-9.-]*\.(?:grph\.xyz|louie\.internal)\b",
    re.IGNORECASE,
)

_ALLOWLIST_PRAGMA = "pragma: allowlist secret"

# Substring, not prefix: "my-fake-key-1234" and "local-dev-key" are placeholders
# too, and a prefix-only test lets them through.
_PLACEHOLDER_MARKERS = (
    "dummy",
    "example",
    "fake",
    "masked",
    "mock",
    "placeholder",
    "redacted",
    "replace",
    "sample",
    "your",
)
_PLACEHOLDER_PREFIXES = ("pk_", "sk_", "test", "local-dev")

_MIN_SECRET_LENGTH = 12
_MIN_SECRET_DISTINCT = 6


def _has_letter_and_digit(value: str) -> bool:
    return any(c.isalpha() for c in value) and any(c.isdigit() for c in value)


def _is_placeholder(value: str) -> bool:
    """True when the literal is obviously not a real credential."""
    candidate = value.strip()
    lowered = candidate.lower()
    if not candidate:
        return True
    # <angle-bracket>, ${ENV_VAR}, {format_slot}
    if candidate.startswith(("<", "${", "{")) and candidate.endswith((">", "}")):
        return True
    if any(marker in lowered for marker in _PLACEHOLDER_MARKERS):
        return True
    if lowered.startswith(_PLACEHOLDER_PREFIXES):
        return True
    if "..." in candidate:  # elided doc sample, e.g. "sk_123..."
        return True
    # Single repeated filler character, e.g. XXXXXXXXXX or ----------
    return len(set(candidate)) <= 1 or set(candidate) <= {"X", "x", "*", ".", "-", "_"}


# A snake_case identifier that names a credential field is a *name*, not a
# value: `{"personal_key_id": 10, "personal_key_secret": 16}` would otherwise
# parse as an assignment of the string "personal_key_secret".
_FIELD_NAME_MARKERS = ("key", "secret", "password", "token", "credential")


def _is_field_name(value: str) -> bool:
    candidate = value.strip()
    return (
        candidate.isidentifier()
        and candidate.islower()
        and any(marker in candidate for marker in _FIELD_NAME_MARKERS)
    )


def _looks_like_secret(value: str) -> bool:
    """True when an off-shape value still has credential-grade entropy.

    Letter **or** digit, not both: a purely numeric key id and a purely
    alphabetic passphrase are both realistic credential formats, and requiring
    the conjunction vetoed them.
    """
    candidate = value.strip()
    if len(candidate) < _MIN_SECRET_LENGTH:
        return False
    if len(set(candidate)) < _MIN_SECRET_DISTINCT:
        return False
    if _is_field_name(candidate):
        return False
    return any(c.isalnum() for c in candidate)


def _tracked_paths(*, staged: bool) -> list[str]:
    # --no-renames: with rename detection on, `git mv clean.py config.py` plus an
    # edit reports only `R`, which --diff-filter=ACM drops — letting a credential
    # through pre-commit via rename+edit.
    command = (
        [
            "git",
            "diff",
            "--cached",
            "--no-renames",
            "--name-only",
            "--diff-filter=ACM",
            "-z",
        ]
        if staged
        else ["git", "ls-files", "-z"]
    )
    output = subprocess.check_output(command)
    return [item.decode("utf-8") for item in output.split(b"\0") if item]


def _read_text(path: str, *, staged: bool) -> str | None:
    """Return decoded text, or None for binaries, symlinks, and unreadable paths."""
    if staged:
        raw = subprocess.check_output(["git", "show", f":{path}"])
    else:
        candidate = Path(path)
        if candidate.is_symlink() or not candidate.is_file():
            return None
        raw = candidate.read_bytes()
    if b"\0" in raw:  # binary
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _allowlisted(lines: Sequence[str], line_number: int) -> bool:
    index = line_number - 1
    return 0 <= index < len(lines) and _ALLOWLIST_PRAGMA in lines[index]


def _find(text: str) -> Iterable[tuple[int, str, str]]:
    """Yield (line, rule, label) for each finding. Never yields the value."""
    lines = text.splitlines()
    seen: set[tuple[int, str]] = set()

    for match in _VALUE_SHAPE.finditer(text):
        value = match.group(1)
        if not _has_letter_and_digit(value) or _is_placeholder(value):
            continue
        line = _line_of(text, match.start())
        if _allowlisted(lines, line):
            continue
        label = next(
            (name for name, width in _SHAPES.items() if width == len(value)),
            "personal key",
        )
        if (line, label) not in seen:
            seen.add((line, label))
            yield line, "value-shape", label

    for match in _KEY_CONTEXT.finditer(text):
        value = match.group("value")
        if _is_placeholder(value):
            continue
        # Skip only if value-shape *actually* reported it. Testing the shape
        # regex alone would drop a numeric-only value: it matches the shape but
        # value-shape rejects it on the letter/digit filter, so it would fall
        # through both rules.
        if _VALUE_SHAPE.fullmatch(value) and _has_letter_and_digit(value):
            continue
        if not _looks_like_secret(value):
            continue  # short/low-entropy mock such as "pk_123" or "MY_KEY_ID"
        line = _line_of(text, match.start())
        if _allowlisted(lines, line):
            continue
        label = match.group("key").lower()
        if (line, label) not in seen:
            seen.add((line, label))
            yield line, "key-context", label

    for match in _INTERNAL_HOSTS.finditer(text):
        line = _line_of(text, match.start())
        if _allowlisted(lines, line):
            continue
        if (line, "internal host") not in seen:
            seen.add((line, "internal host"))
            yield line, "internal-host", "internal host"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reject hard-coded personal keys.")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="scan staged index content instead of the working tree",
    )
    parser.add_argument(
        "--exclude-files",
        default=None,
        metavar="REGEX",
        help=(
            "skip paths matching this regex. Escape hatch for files that cannot "
            "carry a '# pragma: allowlist secret' line, such as an .ipynb data "
            "URI or a CSV row."
        ),
    )
    parser.add_argument("paths", nargs="*", help="explicit paths (default: tracked)")
    args = parser.parse_args(argv)

    excluded = re.compile(args.exclude_files) if args.exclude_files else None
    explicit = bool(args.paths)
    paths = args.paths or _tracked_paths(staged=args.staged)

    failed = False
    for path in paths:
        if excluded is not None and excluded.search(path):
            continue
        try:
            text = _read_text(path, staged=args.staged and not explicit)
        except (OSError, subprocess.CalledProcessError):
            continue
        if text is None:
            continue
        for line, rule, label in _find(text):
            print(
                f"{path}:{line}: hard-coded {label} literal [{rule}]; "
                "use an environment variable or an explicit placeholder",
                file=sys.stderr,
            )
            failed = True

    if failed:
        print(
            "\nValues are intentionally not printed.\n"
            "  Real credential      -> replace with an environment variable or a "
            "placeholder such as <your-personal-key-id>.\n"
            "  Deliberate test fixture -> build it at runtime so no literal exists, "
            'e.g. FAKE = "A1B2C3D4" + "E5F6G7H8"; or append '
            f"'# {_ALLOWLIST_PRAGMA}' on the SAME line.\n"
            "  File that cannot hold a comment (.ipynb data URI, CSV) -> "
            "--exclude-files <regex>.\n"
            "See .secret-patterns.md, 'Writing tests that contain deliberate fake "
            "secrets'.",
            file=sys.stderr,
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
