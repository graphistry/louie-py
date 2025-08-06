#!/bin/bash
# test-secret-detection.sh - Test secret detection functionality
# This script creates temporary test files to verify secret detection works correctly
# Usage: ./scripts/test-secret-detection.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔬 Testing Secret Detection System${NC}"
echo "========================================"

# Create a temporary directory for testing
TEST_DIR=$(mktemp -d -t secret-test-XXXXXX)
trap "rm -rf $TEST_DIR" EXIT

echo -e "${YELLOW}📁 Test directory: $TEST_DIR${NC}"
echo ""

# Function to run a test
run_test() {
    local test_name="$1"
    local file_path="$2"
    local content="$3"
    local should_detect="$4"  # "yes" or "no"
    
    echo -e "${BLUE}Test: $test_name${NC}"
    echo "$content" > "$file_path"
    
    # Stage the file for pre-commit test
    cd "$(dirname "$0")/.."
    cp "$file_path" "$TEST_DIR/test_file.py"
    
    # Run detection
    if uv run detect-secrets scan "$TEST_DIR/test_file.py" 2>/dev/null | grep -q "\"$TEST_DIR/test_file.py\""; then
        detected="yes"
    else
        detected="no"
    fi
    
    if [ "$detected" = "$should_detect" ]; then
        echo -e "${GREEN}  ✅ PASS: Detection result as expected ($detected)${NC}"
        return 0
    else
        echo -e "${RED}  ❌ FAIL: Expected detection=$should_detect, got=$detected${NC}"
        echo "  Content: $content"
        return 1
    fi
}

# Test counter
PASSED=0
FAILED=0

echo -e "${YELLOW}🚨 Testing UNSAFE patterns (should be detected)${NC}"
echo "----------------------------------------"

# Real-looking secrets that SHOULD be detected
run_test "Generic API Key" \
    "$TEST_DIR/api.py" \
    'api_key = "super_secret_api_key_12345"' \
    "yes" && ((PASSED++)) || ((FAILED++))

run_test "Generic Password" \
    "$TEST_DIR/password.py" \
    'password = "mysecretpassword123"' \
    "yes" && ((PASSED++)) || ((FAILED++))

run_test "API Token" \
    "$TEST_DIR/token.py" \
    'api_token = "token_abc123def456ghi789"' \
    "yes" && ((PASSED++)) || ((FAILED++))

run_test "Private Key" \
    "$TEST_DIR/key.py" \
    'private_key = "private_key_secret_value_123"' \
    "yes" && ((PASSED++)) || ((FAILED++))

run_test "Base64 Secret" \
    "$TEST_DIR/b64.py" \
    'secret = "cGFzc3dvcmQ9bXlfc2VjcmV0X3Bhc3N3b3Jk"' \
    "yes" && ((PASSED++)) || ((FAILED++))

echo ""
echo -e "${YELLOW}✅ Testing SAFE patterns (should NOT be detected)${NC}"
echo "----------------------------------------"

# Safe placeholders that should NOT be detected
run_test "XXXX Placeholder" \
    "$TEST_DIR/safe1.py" \
    'API_KEY = "sk-XXXXXXXXXXXXXXXX"' \
    "no" && ((PASSED++)) || ((FAILED++))

run_test "Angle Bracket Placeholder" \
    "$TEST_DIR/safe2.py" \
    'password = "<your-password>"' \
    "no" && ((PASSED++)) || ((FAILED++))

run_test "Token with XXXX" \
    "$TEST_DIR/safe3.py" \
    'token = "token-XXXX-XXXX-XXXX"' \
    "no" && ((PASSED++)) || ((FAILED++))

run_test "Stars Placeholder" \
    "$TEST_DIR/safe4.py" \
    'SECRET = "****"' \
    "no" && ((PASSED++)) || ((FAILED++))

run_test "Example Placeholder" \
    "$TEST_DIR/safe5.py" \
    'key = "your-api-key-here"' \
    "no" && ((PASSED++)) || ((FAILED++))

run_test "Dots Placeholder" \
    "$TEST_DIR/safe6.py" \
    'token = "..."' \
    "no" && ((PASSED++)) || ((FAILED++))

echo ""
echo -e "${YELLOW}🧪 Testing with actual scripts${NC}"
echo "----------------------------------------"

# Test our actual detection script
echo -e "${BLUE}Testing centralized script:${NC}"
if ./scripts/ci/secret-detection.sh > /dev/null 2>&1; then
    echo -e "${GREEN}  ✅ Secret detection script runs successfully${NC}"
    ((PASSED++))
else
    echo -e "${RED}  ❌ Secret detection script failed${NC}"
    ((FAILED++))
fi

# Test the pre-commit wrapper
echo -e "${BLUE}Testing pre-commit wrapper:${NC}"
if ./scripts/pre-commit-secret-check.sh > /dev/null 2>&1; then
    echo -e "${GREEN}  ✅ Pre-commit wrapper runs successfully${NC}"
    ((PASSED++))
else
    echo -e "${RED}  ❌ Pre-commit wrapper failed${NC}"
    ((FAILED++))
fi

# Summary
echo ""
echo "========================================"
echo -e "${BLUE}📊 Test Summary${NC}"
echo "----------------------------------------"
echo -e "  Passed: ${GREEN}$PASSED${NC}"
echo -e "  Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  Some tests failed. Review the output above.${NC}"
    exit 1
fi