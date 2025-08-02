#!/bin/bash
# ruff.sh - Smart wrapper for ruff with sensible defaults
# Usage: ./scripts/ruff.sh [args...]
# No args: runs 'ruff check .' (most common use case)
# With args: passes through to ruff

if [ $# -eq 0 ]; then
    # Smart default: check all files
    echo "🔍 Running ruff check with smart defaults..."
    uv run ruff check .
elif [ "$1" = "--fix" ] && [ $# -eq 1 ]; then
    # User probably meant 'ruff check --fix'
    echo "📝 Fixed your command: 'ruff --fix' → 'ruff check --fix'"
    echo "🔧 Running ruff check --fix..."
    uv run ruff check --fix .
else
    # Pass through all arguments
    uv run ruff "$@"
fi