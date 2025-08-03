#!/bin/bash
# typecheck.sh - Run type checking with mypy
# Usage: ./scripts/ci/typecheck.sh

set -e

# Source common utilities
source "$(dirname "$0")/../common.sh"

# Check prerequisites
check_uv
check_project_root

echo "🔍 Running type checking with mypy..."
uv run mypy .