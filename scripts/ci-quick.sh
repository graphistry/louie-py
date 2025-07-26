#!/bin/bash
# ci-quick.sh - Quick CI checks for rapid development iteration
# Runs essential checks only for fast feedback during development
# Usage: ./scripts/ci-quick.sh

set -e  # Exit on any error

echo "⚡ Running quick CI checks (fast feedback)"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print step headers
print_step() {
    echo ""
    echo -e "${YELLOW}▶ $1${NC}"
    echo "----------------------------------------"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error and exit
print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if uv is available
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

print_step "Quick lint check (errors only)"
./scripts/ruff.sh check --select=F,E . || print_error "Critical linting errors found"
print_success "No critical errors"

print_step "Running tests (fail fast)"
./scripts/pytest.sh -x --tb=short || print_error "Tests failed"
print_success "Tests passed"

echo ""
echo -e "${GREEN}⚡ Quick checks passed! Continue development${NC}"
echo "💡 Run ./scripts/ci-local.sh for full CI validation before push"
echo "=========================================="