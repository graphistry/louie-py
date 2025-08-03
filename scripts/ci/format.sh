#!/bin/bash
# format.sh - Check code formatting with ruff
# Usage: ./scripts/ci/format.sh [--fix]

set -e

# Source common utilities
source "$(dirname "$0")/../common.sh"

# Check prerequisites
check_uv
check_project_root

# Parse arguments
FIX_MODE=false
if [[ "$1" == "--fix" ]]; then
    FIX_MODE=true
fi

if $FIX_MODE; then
    echo "🎨 Formatting code with ruff..."
    uv run ruff format .
else
    echo "🎨 Checking code format with ruff..."
    uv run ruff format --check .
fi