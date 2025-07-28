#!/bin/bash
# ci-quick.sh - Quick CI checks for rapid development iteration
# Runs essential checks only for fast feedback during development
# Usage: ./scripts/ci-quick.sh

set -e  # Exit on any error

# Source common utilities
source "$(dirname "$0")/common.sh"

echo "⚡ Running quick CI checks (fast feedback)"
echo "=========================================="

# Check prerequisites
check_uv
check_project_root

print_step "Quick lint check (errors only)"
./bin/uv run ruff check . || print_error "Critical linting errors found"
print_success "No critical errors"

print_step "Validate ReadTheDocs config"
./scripts/validate-readthedocs.sh || print_error "ReadTheDocs config is invalid"
print_success "ReadTheDocs config valid"

print_step "Running tests (fail fast)"
./bin/uv run pytest -x --tb=short || print_error "Tests failed"
print_success "Tests passed"

echo ""
echo -e "${GREEN}⚡ Quick checks passed! Continue development${NC}"
echo "💡 Run ./scripts/ci-local.sh for full CI validation before push"
echo "=========================================="