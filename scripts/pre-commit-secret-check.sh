#!/bin/bash
# pre-commit-secret-check.sh - Wrapper for pre-commit hook
# This script is called by pre-commit and uses the centralized secret detection

# Run the centralized script in check-only mode
exec "$(dirname "$0")/ci/secret-detection.sh" --check-only