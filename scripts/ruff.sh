#!/bin/bash
# ruff.sh - Smart wrapper for ruff with sensible defaults
# Usage: ./scripts/ruff.sh [args...]
# No args: runs 'ruff check .' (most common use case)
# With args: passes through to ruff

if [ $# -eq 0 ]; then
    # Smart default: check all files
    echo "🔍 Running ruff check with smart defaults..."
    uv run ruff check .
else
    # Pass through all arguments
    uv run ruff "$@"
fi