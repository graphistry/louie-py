#!/bin/bash
# common.sh - Shared utilities for louie-py scripts
# Source this file in other scripts: source "$(dirname "$0")/common.sh"

# Color constants for consistent output
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export NC='\033[0m' # No Color

# Print functions for consistent formatting
print_step() {
    echo ""
    echo -e "${YELLOW}▶ $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if uv is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    fi
}

# Check if we're in project root
check_project_root() {
    if [ ! -f "pyproject.toml" ]; then
        print_error "Must run from project root (no pyproject.toml found)"
    fi
}

# Create and setup temporary directory with cleanup
setup_temp_dir() {
    local prefix="${1:-louie-test}"
    TEST_DIR=$(mktemp -d -t "${prefix}-XXXXXX")
    echo "📁 Created test directory: $TEST_DIR"
    
    # Setup cleanup trap
    cleanup() {
        echo "🧹 Cleaning up test environment..."
        rm -rf "$TEST_DIR"
    }
    trap cleanup EXIT
    
    echo "$TEST_DIR"
}