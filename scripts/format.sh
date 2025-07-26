#!/bin/bash
# format.sh - Smart wrapper for ruff format with sensible defaults
# Usage: ./scripts/format.sh [args...]
# No args: formats all files in place
# With args: passes through to ruff format

if [ $# -eq 0 ]; then
    # Smart default: format all files in place
    echo "✨ Formatting all files with ruff..."
    uv run ruff format .
else
    # Pass through all arguments
    uv run ruff format "$@"
fi