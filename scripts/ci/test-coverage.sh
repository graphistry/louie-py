#!/bin/bash
# test-coverage.sh - Run tests with coverage reporting
# Usage: ./scripts/ci/test-coverage.sh [--threshold=85] [--fail-fast] [pytest-args...]

set -e

# Source common utilities
source "$(dirname "$0")/../common.sh"

# Check prerequisites
check_uv
check_project_root

# Default values
COVERAGE_THRESHOLD=85
FAIL_FAST=""
PYTEST_ARGS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --threshold=*)
            COVERAGE_THRESHOLD="${1#*=}"
            shift
            ;;
        --fail-fast)
            FAIL_FAST="-x"
            shift
            ;;
        *)
            PYTEST_ARGS+=("$1")
            shift
            ;;
    esac
done

echo "🧪 Running tests with coverage (threshold: ${COVERAGE_THRESHOLD}%)..."

# Build pytest command
PYTEST_CMD=(
    "uv" "run" "python" "-m" "pytest"
    "--cov=louieai"
    "--cov-report=term"
    "--cov-report=xml"
    "--cov-fail-under=${COVERAGE_THRESHOLD}"
)

# Add fail-fast if requested
if [[ -n "$FAIL_FAST" ]]; then
    PYTEST_CMD+=("$FAIL_FAST" "--tb=short")
fi

# Add any additional pytest args
if [[ ${#PYTEST_ARGS[@]} -gt 0 ]]; then
    PYTEST_CMD+=("${PYTEST_ARGS[@]}")
fi

# Execute pytest
"${PYTEST_CMD[@]}"