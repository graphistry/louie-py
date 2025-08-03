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

# Default coverage threshold
# TODO: Increase test coverage back to 85% in future release
DEFAULT_THRESHOLD=80

# Use the centralized test-coverage script
if [ $# -eq 0 ]; then
    # Smart default: full coverage reporting with threshold
    echo "🧪 Running pytest with smart defaults (coverage + threshold)..."
    ./scripts/ci/test-coverage.sh --threshold=$DEFAULT_THRESHOLD
else
    # Check if coverage args already provided
    if echo "$*" | grep -q "\--cov"; then
        # User provided coverage args, pass through directly to pytest
        uv run python -m pytest "$@"
    else
        # Use centralized coverage script with user args
        echo "🧪 Running pytest with coverage defaults + your args..."
        ./scripts/ci/test-coverage.sh --threshold=0 "$@"
    fi
fi