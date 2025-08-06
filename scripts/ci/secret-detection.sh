#!/bin/bash
# secret-detection.sh - Centralized secret detection using detect-secrets
# This script is used by both CI and pre-commit hooks
# Usage: ./scripts/ci/secret-detection.sh [--check-only]
#
# To test changes to this script:
#   ./scripts/test-secret-detection.sh
# See also: tests/secret_patterns_reference.py for pattern examples

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print error and exit
print_error() {
    echo -e "${RED}❌ $1${NC}" >&2
    exit 1
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" >&2
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Check if we're in check-only mode (for pre-commit)
CHECK_ONLY=false
if [ "$1" == "--check-only" ]; then
    CHECK_ONLY=true
fi

# Ensure we're in project root
if [ ! -f "pyproject.toml" ]; then
    print_error "Must run from project root (where pyproject.toml exists)"
fi

# Check if detect-secrets is available
if ! command -v detect-secrets &> /dev/null; then
    # Try with uv run
    if ! uv run detect-secrets --version &> /dev/null 2>&1; then
        print_error "detect-secrets not found. Install with: uv pip install detect-secrets"
    fi
    DETECT_SECRETS="uv run detect-secrets"
else
    DETECT_SECRETS="detect-secrets"
fi

# Ensure baseline exists
if [ ! -f ".secrets.baseline" ]; then
    print_warning "No .secrets.baseline found. Creating initial baseline..."
    $DETECT_SECRETS scan --exclude-files '^(plans/|tmp/)' > .secrets.baseline
    print_success "Created .secrets.baseline - please review and commit"
    exit 0
fi

if [ "$CHECK_ONLY" == true ]; then
    # Pre-commit mode: just check for new secrets
    echo "🔍 Checking for secrets in staged files..."
    
    # Get list of staged files (excluding plans/ and tmp/)
    STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -v '^plans/' | grep -v '^tmp/' || true)
    
    if [ -z "$STAGED_FILES" ]; then
        print_success "No files to check"
        exit 0
    fi
    
    # Check staged files for secrets
    TEMP_BASELINE=$(mktemp)
    echo "$STAGED_FILES" | xargs $DETECT_SECRETS scan --baseline .secrets.baseline > "$TEMP_BASELINE" 2>/dev/null || true
    
    # Check if any new secrets were detected
    if [ -s "$TEMP_BASELINE" ]; then
        NEW_SECRETS=$(python3 -c "
import json
import sys
with open('$TEMP_BASELINE') as f:
    data = json.load(f)
    total = sum(len(secrets) for secrets in data.get('results', {}).values())
    sys.exit(0 if total == 0 else 1)
" 2>/dev/null || echo "1")
        
        rm "$TEMP_BASELINE"
        
        if [ "$NEW_SECRETS" == "1" ]; then
            print_error "New secrets detected! Use clear placeholders like 'sk-XXXXXXXX' or '<your-password>'"
        fi
    fi
    
    rm -f "$TEMP_BASELINE"
    print_success "No secrets detected"
else
    # CI mode: full scan
    echo "🔍 Running full secret detection scan..."
    
    # Check for new secrets not in baseline
    echo "Checking for new secrets not in baseline..."
    $DETECT_SECRETS scan --baseline .secrets.baseline --exclude-files '^(plans/|tmp/)' || {
        print_error "New secrets detected! Either remove them or update baseline with: detect-secrets scan --baseline .secrets.baseline"
    }
    
    # Verify no high-confidence secrets
    echo "Verifying no high-confidence secrets..."
    $DETECT_SECRETS scan --baseline .secrets.baseline --only-verified --exclude-files '^(plans/|tmp/)' || {
        print_error "High-confidence secrets detected! These must be removed."
    }
    
    print_success "Secret detection passed - no new secrets found"
fi