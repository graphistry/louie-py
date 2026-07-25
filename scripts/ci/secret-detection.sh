#!/bin/bash
# secret-detection.sh - Centralized secret detection using detect-secrets
# This script is used by both CI and pre-commit hooks
# Usage: ./scripts/ci/secret-detection.sh [--check-only]
#
# To test changes to this script:
#   ./scripts/test-secret-detection.sh
# See also: tests/secret_patterns_reference.py for pattern examples

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print error and exit
print_error() {
    echo -e "${RED}❌ $1${NC}" >&2
    exit 1
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" >&2
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Check if we're in check-only mode (for pre-commit)
CHECK_ONLY=false
if [ "$1" == "--check-only" ]; then
    CHECK_ONLY=true
fi

# Ensure we're in project root
if [ ! -f "pyproject.toml" ]; then
    print_error "Must run from project root (where pyproject.toml exists)"
fi

# detect-secrets entropy heuristics can miss short Graphistry personal keys.
# This deterministic check reports only key names and locations, never values.
# In --check-only (pre-commit) mode scan the staged index, so a credential
# cannot be committed even when the working tree has already been cleaned.
CREDENTIAL_SCAN_ARGS=()
if [ "$CHECK_ONLY" == true ]; then
    CREDENTIAL_SCAN_ARGS+=(--staged)
fi
python3 scripts/ci/check_credential_literals.py "${CREDENTIAL_SCAN_ARGS[@]}" || {
    print_error "Hard-coded Graphistry personal key detected"
}

# Check if detect-secrets is available
if ! command -v detect-secrets &> /dev/null; then
    # Try with uv run. `--frozen` is required: a bare `uv run` re-resolves and
    # rewrites uv.lock, silently dropping its `[options] exclude-newer` pin.
    # That is the source of the stray uv.lock diff that keeps reappearing after
    # running the security or lint scripts.
    if ! uv run --frozen detect-secrets --version &> /dev/null 2>&1; then
        print_error "detect-secrets not found. Install with: uv pip install detect-secrets"
    fi
    DETECT_SECRETS="uv run --frozen detect-secrets"
else
    DETECT_SECRETS="detect-secrets"
fi

# Ensure baseline exists.
#
# This must NOT exit 0. Generating a baseline accepts whatever is currently in
# the tree, so `rm .secrets.baseline && ./secret-detection.sh` used to pass while
# permanently whitelisting any secret present — the same "always exit 0" shape
# this script exists to eliminate. Generate, then fail so a human reviews it.
if [ ! -f ".secrets.baseline" ]; then
    print_warning "No .secrets.baseline found. Creating initial baseline..."
    $DETECT_SECRETS scan --exclude-files '^(plans/|tmp/|\.secrets\.baseline$)' > .secrets.baseline
    print_error "Created .secrets.baseline from the current tree. Review it (it accepts everything found), commit it, then re-run."
fi

if [ "$CHECK_ONLY" == true ]; then
    # Pre-commit mode: just check for new secrets
    echo "🔍 Checking for secrets in staged files..."
    
    # NUL-delimited end to end. The previous newline+`xargs` pipeline word-split
    # on spaces, and detect-secrets exits 0 with empty results for a path that
    # does not exist — so a staged file named `zz spaced.py` scanned nothing and
    # the gate reported success.
    #
    # --no-renames: with rename detection on, `git mv a.py b.py` plus an edit
    # reports only `R`, which --diff-filter=ACM drops — a working bypass that
    # let a secret reach a commit with a green hook.
    TEMP_LIST=$(mktemp)
    TEMP_SCAN=$(mktemp)
    trap 'rm -f "$TEMP_LIST" "$TEMP_SCAN"' EXIT

    git diff --cached --no-renames --name-only --diff-filter=ACM -z \
        | python3 -c '
import sys
skip = ("plans/", "tmp/")
data = sys.stdin.buffer.read().split(b"\0")
keep = [
    p for p in data
    if p and p != b".secrets.baseline"
    and not any(p.startswith(s.encode()) for s in skip)
]
# NUL-TERMINATE, do not NUL-separate. `read -r -d ""` only emits a field when
# it sees the delimiter, so joining instead of terminating silently drops the
# last staged file — which meant it was never scanned.
sys.stdout.buffer.write(b"".join(p + b"\0" for p in keep))
' > "$TEMP_LIST"

    if [ ! -s "$TEMP_LIST" ]; then
        print_success "No files to check"
        exit 0
    fi

    # Materialise the INDEX, not the working tree. detect-secrets scans files on
    # disk, so `git add <secret>` followed by cleaning or deleting the file made
    # the hook pass while the commit still carried the secret — the same evasion
    # `--staged` closes for the personal-key rule, but it applied to every
    # detect-secrets finding class.
    STAGE_DIR=$(mktemp -d)
    trap 'rm -rf "$TEMP_LIST" "$TEMP_SCAN" "$STAGE_DIR"' EXIT
    while IFS= read -r -d '' staged_path; do
        mkdir -p "$STAGE_DIR/$(dirname "$staged_path")"
        git show ":$staged_path" > "$STAGE_DIR/$staged_path" 2>/dev/null || true
    done < "$TEMP_LIST"

    # Scan WITHOUT --baseline. `scan --baseline <f>` updates the file in place,
    # writes nothing to stdout, and exits 0 whatever it finds — so the previous
    # `if [ -s "$TEMP_SCAN" ]` guard tested an always-empty file and skipped the
    # check entirely. Compare against the baseline explicitly instead.
    # stderr is deliberately NOT suppressed: hiding it is what made the
    # path-mangling failure above invisible.
    ( cd "$STAGE_DIR" && $DETECT_SECRETS scan --all-files ) > "$TEMP_SCAN"

    python3 scripts/ci/check_new_secrets.py \
        --baseline .secrets.baseline --scan "$TEMP_SCAN" || {
        print_error "New secrets detected! Use clear placeholders like 'sk-XXXXXXXX' or '<your-password>'"
    }

    print_success "No secrets detected"
else
    # CI mode: full scan
    echo "🔍 Running full secret detection scan..."

    # Scan WITHOUT --baseline, then diff against it. `scan --baseline <f>` is an
    # update command: it rewrites the file and exits 0 regardless of findings, so
    # both `|| print_error` branches below were unreachable and this gate had
    # never once failed — a known-live credential passed it for ~12 months.
    TEMP_SCAN=$(mktemp)
    trap 'rm -f "$TEMP_SCAN"' EXIT

    echo "Checking for new secrets not in baseline..."
    $DETECT_SECRETS scan --exclude-files '^(plans/|tmp/|\.secrets\.baseline$)' > "$TEMP_SCAN"

    python3 scripts/ci/check_new_secrets.py \
        --baseline .secrets.baseline --scan "$TEMP_SCAN" || {
        print_error "New secrets detected! Either remove them, or re-baseline with: detect-secrets scan > .secrets.baseline (and review the diff)"
    }

    print_success "Secret detection passed - no new secrets found"
fi
