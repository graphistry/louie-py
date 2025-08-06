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

# Source common utilities for shared functions
source "$(dirname "$0")/common.sh"

print_step "Environment sanity check"
# Ensure we have .venv and it's using the right Python
if [ ! -f ".venv/bin/python" ]; then
    print_error ".venv not found - run './bin/uv venv' first"
fi

# Check we're using venv Python, not host Python
VENV_PYTHON_VERSION=$(./bin/uv run python --version 2>&1 | cut -d' ' -f2)
HOST_PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)

if [ "$VENV_PYTHON_VERSION" == "$HOST_PYTHON_VERSION" ]; then
    echo "⚠️  WARNING: venv Python ($VENV_PYTHON_VERSION) same as host Python ($HOST_PYTHON_VERSION)"
    echo "This might indicate environment issues"
fi

echo "✓ Using venv Python: $VENV_PYTHON_VERSION"
echo "✓ Host Python: $HOST_PYTHON_VERSION"
print_success "Environment verified"

print_step "Installing dependencies with uv"
./scripts/ci/install-deps.sh || print_error "Failed to install dependencies"
print_success "Dependencies installed"

print_step "Secret detection scan"
./scripts/ci/secret-detection.sh || print_error "Secrets detected"
print_success "No secrets found"

print_step "Linting with ruff"
./scripts/ci/lint.sh || print_error "Linting failed"
print_success "Linting passed"

print_step "Format checking with ruff"
./scripts/ci/format.sh || print_error "Format check failed"
print_success "Format check passed"

print_step "Type checking with mypy"
./scripts/ci/typecheck.sh || print_error "Type checking failed"  
print_success "Type checking passed"

print_step "Running tests with coverage (85% threshold)"
./scripts/ci/test-coverage.sh --threshold=85 -q || print_error "Tests or coverage threshold failed"
print_success "Tests and coverage passed"

print_step "Validate ReadTheDocs config"
./scripts/ci/validate-rtd.sh || print_error "ReadTheDocs config is invalid"
print_success "ReadTheDocs config valid"

print_step "Building documentation with MkDocs (including notebooks)"
./scripts/ci/docs-build.sh || print_error "Documentation build failed"
print_success "Documentation built successfully"

echo ""
echo -e "${GREEN}🎉 All CI checks passed! Ready for push/PR${NC}"
echo "================================================"