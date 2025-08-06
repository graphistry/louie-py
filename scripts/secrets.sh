#!/bin/bash
# secrets.sh - Run secret detection manually
# Usage: ./scripts/secrets.sh [--update-baseline]

set -e

# Check for update baseline flag
if [ "$1" == "--update-baseline" ]; then
    echo "📝 Updating secrets baseline..."
    uv run detect-secrets scan --exclude-files '^(plans/|tmp/)' > .secrets.baseline
    echo "✅ Baseline updated. Review changes and commit if appropriate."
else
    # Run the standard secret detection
    exec "$(dirname "$0")/ci/secret-detection.sh"
fi