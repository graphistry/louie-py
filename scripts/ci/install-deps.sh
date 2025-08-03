#!/bin/bash
# install-deps.sh - Install project dependencies
# Usage: ./scripts/ci/install-deps.sh [--dev]

set -e

# Source common utilities
source "$(dirname "$0")/../common.sh"

# Check prerequisites
check_uv
check_project_root

# Parse arguments
DEV_MODE=true
if [[ "$1" == "--no-dev" ]]; then
    DEV_MODE=false
fi

if $DEV_MODE; then
    echo "📦 Installing dependencies with development extras..."
    uv pip install -e ".[dev]"
else
    echo "📦 Installing production dependencies only..."
    uv pip install -e "."
fi