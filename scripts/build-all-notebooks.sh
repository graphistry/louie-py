#!/bin/bash
# Build all notebooks in the getting-started directory
# Usage: ./scripts/build-all-notebooks.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTEBOOKS_DIR="docs/getting-started/notebooks"

# Check if notebooks directory exists
if [ ! -d "$NOTEBOOKS_DIR" ]; then
    echo "❌ Notebooks directory not found: $NOTEBOOKS_DIR"
    exit 1
fi

echo "🔨 Building all notebooks in $NOTEBOOKS_DIR"
echo "=" * 50

# Track success/failure
SUCCESS_COUNT=0
FAIL_COUNT=0
FAILED_NOTEBOOKS=()

# Find all .ipynb files
for notebook in "$NOTEBOOKS_DIR"/*.ipynb; do
    if [ -f "$notebook" ]; then
        echo ""
        echo "📓 Processing: $(basename "$notebook")"
        echo "-" * 40
        
        if "$SCRIPT_DIR/build-notebook.sh" "$notebook"; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            FAIL_COUNT=$((FAIL_COUNT + 1))
            FAILED_NOTEBOOKS+=("$(basename "$notebook")")
        fi
    fi
done

echo ""
echo "=" * 50
echo "📊 Summary:"
echo "  ✅ Successfully built: $SUCCESS_COUNT notebooks"
echo "  ❌ Failed: $FAIL_COUNT notebooks"

if [ $FAIL_COUNT -gt 0 ]; then
    echo ""
    echo "Failed notebooks:"
    printf '  - %s\n' "${FAILED_NOTEBOOKS[@]}"
    exit 1
fi

echo ""
echo "✅ All notebooks built successfully!"