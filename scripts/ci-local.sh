#!/bin/bash
# ci-local.sh - Run full CI pipeline locally using uv
# This script replicates the exact CI workflow for local development
# Usage: ./scripts/ci-local.sh

set -e  # Exit on any error

echo "🚀 Running local CI simulation (full pipeline)"
echo "================================================"

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

print_step "Installing dependencies with uv"
uv pip install -e ".[dev]" || print_error "Failed to install dependencies"
print_success "Dependencies installed"

print_step "Linting with ruff"
./scripts/ruff.sh || print_error "Linting failed"
print_success "Linting passed"

print_step "Format checking with ruff"
./scripts/format.sh --check || print_error "Format check failed"
print_success "Format check passed"

print_step "Validate ReadTheDocs config"
./scripts/validate-readthedocs.sh || print_error "ReadTheDocs config is invalid"
print_success "ReadTheDocs config valid"

print_step "Type checking with mypy"
./scripts/mypy.sh || print_error "Type checking failed"
print_success "Type checking passed"

print_step "Running tests with coverage (85% threshold)"
./scripts/pytest.sh -q --cov-report=xml --cov-fail-under=85 || print_error "Tests or coverage threshold failed"
print_success "Tests and coverage passed"

echo ""
echo -e "${GREEN}🎉 All CI checks passed! Ready for push/PR${NC}"
echo "================================================"