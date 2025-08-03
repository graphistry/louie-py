#!/bin/bash
# validate-rtd.sh - Validate ReadTheDocs configuration
# Usage: ./scripts/ci/validate-rtd.sh

set -e

# Source common utilities
source "$(dirname "$0")/../common.sh"

# Check prerequisites
check_project_root

echo "📖 Validating ReadTheDocs configuration..."

# Just call the existing script for now
"$(dirname "$0")/../validate-readthedocs.sh"