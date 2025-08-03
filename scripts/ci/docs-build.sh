#!/bin/bash
# docs-build.sh - Build documentation with MkDocs
# Usage: ./scripts/ci/docs-build.sh [--serve]

set -e

# Source common utilities
source "$(dirname "$0")/../common.sh"

# Check prerequisites
check_uv
check_project_root

# Parse arguments
SERVE_MODE=false
if [[ "$1" == "--serve" ]]; then
    SERVE_MODE=true
fi

echo "📚 Installing documentation dependencies..."
uv pip install -r requirements-docs.txt > /dev/null 2>&1 || {
    echo "❌ Failed to install docs dependencies"
    exit 1
}

if $SERVE_MODE; then
    echo "📚 Starting MkDocs development server..."
    uv run mkdocs serve
else
    echo "📚 Building documentation with MkDocs..."
    uv run mkdocs build --strict
fi