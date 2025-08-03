#!/bin/bash
# lint.sh - Run linting checks with ruff
# Usage: ./scripts/ci/lint.sh [--errors-only]

set -e

# Source common utilities
source "$(dirname "$0")/../common.sh"

# Check prerequisites
check_uv
check_project_root

# Parse arguments
ERRORS_ONLY=false
if [[ "$1" == "--errors-only" ]]; then
    ERRORS_ONLY=true
fi

if $ERRORS_ONLY; then
    echo "🔍 Running ruff lint check (errors only)..."
    uv run ruff check . --select=E,F
else
    echo "🔍 Running full ruff lint check..."
    uv run ruff check .
fi