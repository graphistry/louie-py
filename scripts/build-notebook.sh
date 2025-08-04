#!/bin/bash
# Build notebook with environment authentication
# Usage: ./scripts/build-notebook.sh path/to/notebook.ipynb

set -e

NOTEBOOK_PATH="$1"
if [ -z "$NOTEBOOK_PATH" ]; then
    echo "Usage: $0 path/to/notebook.ipynb"
    exit 1
fi

# Check for required environment variables
# Note: This notebook uses Graphistry personal keys
MISSING_VARS=()

# Check Graphistry personal key vars
if grep -q "graphistry.register" "$NOTEBOOK_PATH" 2>/dev/null; then
    if [ -z "$GRAPHISTRY_PERSONAL_KEY_ID" ]; then MISSING_VARS+=("GRAPHISTRY_PERSONAL_KEY_ID"); fi
    if [ -z "$GRAPHISTRY_PERSONAL_KEY_SECRET" ]; then MISSING_VARS+=("GRAPHISTRY_PERSONAL_KEY_SECRET"); fi
    if [ -z "$GRAPHISTRY_ORG_NAME" ]; then MISSING_VARS+=("GRAPHISTRY_ORG_NAME"); fi
fi

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "Error: Missing required environment variables:"
    printf '  - %s\n' "${MISSING_VARS[@]}"
    echo ""
    echo "Set them before running this script:"
    echo "  export GRAPHISTRY_PERSONAL_KEY_ID='your_key_id'"
    echo "  export GRAPHISTRY_PERSONAL_KEY_SECRET='your_key_secret'"
    echo "  export GRAPHISTRY_ORG_NAME='your_org_name'"
    echo ""
    echo "Optional:"
    echo "  export GRAPHISTRY_SERVER='hub.graphistry.com'  # defaults to hub"
    echo "  export LOUIE_SERVER='https://den.louie.ai'     # defaults to den"
    echo ""
    echo "Get your personal key at: https://hub.graphistry.com/users/personal/key/"
    exit 1
fi

echo "🔨 Building notebook: $NOTEBOOK_PATH"

# Create backup
cp "$NOTEBOOK_PATH" "${NOTEBOOK_PATH}.backup"

# Execute notebook
echo "📓 Executing notebook..."
# Use uv if available for correct Python version, otherwise fall back to jupyter
if command -v uv &> /dev/null; then
    JUPYTER_CMD="uv run jupyter execute"
else
    JUPYTER_CMD="jupyter execute"
fi

if ! $JUPYTER_CMD "$NOTEBOOK_PATH" --inplace; then
    echo "❌ Execution failed, restoring backup"
    mv "${NOTEBOOK_PATH}.backup" "$NOTEBOOK_PATH"
    exit 1
fi

# Clean sensitive outputs using helper script
echo "🔍 Cleaning sensitive outputs..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! python3 "$SCRIPT_DIR/notebook-utils/clean-notebook-outputs.py" "$NOTEBOOK_PATH"; then
    echo "❌ Failed to clean notebook outputs, restoring backup"
    mv "${NOTEBOOK_PATH}.backup" "$NOTEBOOK_PATH"
    exit 1
fi

# Validate the notebook
echo "🔍 Validating notebook..."
if ! python3 "$SCRIPT_DIR/notebook-utils/validate-notebook.py" "$NOTEBOOK_PATH"; then
    echo "⚠️  Validation issues found (see above)"
fi

rm "${NOTEBOOK_PATH}.backup"
echo "✅ Notebook built successfully"