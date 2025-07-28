#!/bin/bash
# pytest.sh - Smart wrapper for pytest with sensible defaults
# Usage: ./scripts/pytest.sh [args...]
# No args: runs with coverage and threshold (production-ready defaults)
# With args: adds common smart defaults unless overridden

# Source common utilities
source "$(dirname "$0")/common.sh"

# Ensure we're using the correct Python environment
check_uv
check_project_root

# Use python -m pytest to ensure correct Python interpreter
if [ $# -eq 0 ]; then
    # Smart default: full coverage reporting with threshold
    echo "🧪 Running pytest with smart defaults (coverage + threshold)..."
    uv run python -m pytest --cov=louieai --cov-report=term --cov-fail-under=75
else
    # Check if coverage args already provided
    if echo "$*" | grep -q "\--cov"; then
        # User provided coverage args, pass through as-is
        uv run python -m pytest "$@"
    else
        # Add smart coverage defaults to user args
        echo "🧪 Running pytest with coverage defaults + your args..."
        uv run python -m pytest --cov=louieai --cov-report=term "$@"
    fi
fi