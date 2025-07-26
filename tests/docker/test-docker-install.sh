#!/bin/bash
# test-docker-install.sh - Test installation in Docker containers

set -e  # Exit on any error

echo "🐳 Testing Docker-based installations"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project directory
PROJECT_DIR=$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")
cd "$PROJECT_DIR"

# Build the wheel first
echo ""
echo "🏗️  Building package wheel..."
python -m build . > /dev/null 2>&1

# Find the built wheel
WHEEL_FILE=$(ls -t dist/*.whl | head -1)
if [ -z "$WHEEL_FILE" ]; then
    echo -e "${RED}❌ No wheel file found in dist/${NC}"
    exit 1
fi
WHEEL_NAME=$(basename "$WHEEL_FILE")
echo "📦 Found wheel: $WHEEL_NAME"

# Test pip installation
echo ""
echo "🔧 Testing pip installation in Docker..."
docker build \
    --build-arg WHEEL_FILE="$WHEEL_FILE" \
    -f tests/docker/Dockerfile.pip \
    -t louieai-test-pip \
    .

echo ""
echo "🏃 Running pip container test..."
docker run --rm louieai-test-pip

# Test uv installation
echo ""
echo "🔧 Testing uv installation in Docker..."
docker build \
    --build-arg WHEEL_FILE="$WHEEL_FILE" \
    -f tests/docker/Dockerfile.uv \
    -t louieai-test-uv \
    .

echo ""
echo "🏃 Running uv container test..."
docker run --rm louieai-test-uv

# Cleanup
echo ""
echo "🧹 Cleaning up Docker images..."
docker rmi louieai-test-pip louieai-test-uv || true

echo ""
echo -e "${GREEN}🎉 All Docker installation tests PASSED!${NC}"
echo "===================================="