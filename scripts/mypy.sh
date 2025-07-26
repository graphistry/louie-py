#!/bin/bash
# mypy.sh - Smart wrapper for mypy with sensible defaults
# Usage: ./scripts/mypy.sh [args...]
# No args: runs 'mypy .' (most common use case)
# With args: passes through to mypy

if [ $# -eq 0 ]; then
    # Smart default: check all files
    echo "🔍 Running mypy with smart defaults..."
    uv run mypy .
else
    # Pass through all arguments
    uv run mypy "$@"
fi