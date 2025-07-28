#!/usr/bin/env bash
# Run tests with appropriate configuration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source common utilities
source "$SCRIPT_DIR/common.sh"

cd "$PROJECT_ROOT"

# Default values
TEST_MODE="${LOUIE_TEST_MODE:-unit}"
COVERAGE="${COVERAGE:-false}"
VERBOSE="${VERBOSE:-false}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_MODE="unit"
            shift
            ;;
        --integration)
            TEST_MODE="integration"
            shift
            ;;
        --all)
            TEST_MODE="all"
            shift
            ;;
        --coverage)
            COVERAGE="true"
            shift
            ;;
        --verbose|-v)
            VERBOSE="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit          Run only unit tests (default)"
            echo "  --integration   Run only integration tests"
            echo "  --all           Run all tests"
            echo "  --coverage      Generate coverage report"
            echo "  --verbose, -v   Verbose output"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  LOUIE_TEST_MODE    Test mode (unit/integration/all)"
            echo "  GRAPHISTRY_SERVER  Server URL for integration tests"
            echo "  GRAPHISTRY_USERNAME Username for integration tests"
            echo "  GRAPHISTRY_PASSWORD Password for integration tests"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build pytest arguments
PYTEST_ARGS=()

# Add verbosity
if [[ "$VERBOSE" == "true" ]]; then
    PYTEST_ARGS+=("-v")
fi

# Add coverage
if [[ "$COVERAGE" == "true" ]]; then
    PYTEST_ARGS+=("--cov=louieai" "--cov-report=term-missing")
fi

# Determine which tests to run
case "$TEST_MODE" in
    unit)
        echo "🧪 Running unit tests..."
        PYTEST_ARGS+=("-m" "unit" "tests/unit/")
        ;;
    integration)
        echo "🌐 Running integration tests..."
        # Check for credentials
        if [[ -z "${GRAPHISTRY_USERNAME:-}" ]] || [[ -z "${GRAPHISTRY_PASSWORD:-}" ]]; then
            echo "⚠️  Warning: Integration tests require credentials"
            echo "   Set GRAPHISTRY_USERNAME and GRAPHISTRY_PASSWORD environment variables"
            echo "   Or create a .env file with these values"
        fi
        PYTEST_ARGS+=("-m" "integration" "tests/integration/")
        ;;
    all)
        echo "🚀 Running all tests..."
        PYTEST_ARGS+=("tests/")
        ;;
    *)
        echo "Invalid test mode: $TEST_MODE"
        exit 1
        ;;
esac

# Load environment variables from .env if it exists
if [[ -f .env ]]; then
    echo "📋 Loading environment from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Export test mode
export LOUIE_TEST_MODE="$TEST_MODE"

# Run tests
echo "Running: python -m pytest ${PYTEST_ARGS[*]}"
python -m pytest "${PYTEST_ARGS[@]}"

echo "✅ Tests completed"