#!/bin/bash
# test-secret-detection.sh - Test secret detection functionality
# This script creates temporary test files to verify secret detection works correctly
# Usage: ./scripts/test-secret-detection.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo -e "${BLUE}🔬 Testing Secret Detection System${NC}"
echo "========================================"

# Create a temporary directory for testing
TEST_DIR=$(mktemp -d -t secret-test-XXXXXX)
trap 'rm -rf "$TEST_DIR"' EXIT

echo -e "${YELLOW}📁 Test directory: $TEST_DIR${NC}"
echo ""

PASSED=0
FAILED=0

# NOTE: `((PASSED++))` returns a non-zero status when the variable is 0, which
# under `set -e` aborted this script and made the first passing test increment
# FAILED via the `||` branch. Always use the assignment form below.
pass() {
    PASSED=$((PASSED + 1))
    echo -e "${GREEN}  ✅ PASS: $1${NC}"
}

fail() {
    FAILED=$((FAILED + 1))
    echo -e "${RED}  ❌ FAIL: $1${NC}"
}

# Run detect-secrets over a single file.
#
# NOTE: detect-secrets only reports files located under the current working
# directory. The previous version scanned an absolute path in /tmp while cd'ed
# to the repo root, so every scan came back empty and all five "unsafe"
# fixtures silently looked undetected. Scan from inside TEST_DIR instead.
# NOTE: `--frozen` is required. A bare `uv run` re-resolves and rewrites
# uv.lock, silently dropping its `[options] exclude-newer` pin — that is the
# source of the "incidental uv.lock delta" that keeps reappearing in this repo.
detect_secrets_finds() {
    local relative_file="$1"
    (
        cd "$TEST_DIR"
        uv run --frozen --project "$REPO_ROOT" detect-secrets scan "$relative_file" \
            2>/dev/null
    ) | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("results") else 1)'
}

# Run a detect-secrets expectation test.
run_test() {
    local test_name="$1"
    local content="$2"
    local should_detect="$3" # "yes" or "no"

    echo -e "${BLUE}Test: $test_name${NC}"
    printf '%s\n' "$content" > "$TEST_DIR/test_file.py"

    local detected="no"
    if detect_secrets_finds "test_file.py"; then
        detected="yes"
    fi

    if [ "$detected" = "$should_detect" ]; then
        pass "Detection result as expected ($detected)"
    else
        fail "Expected detection=$should_detect, got=$detected"
    fi
}

# Run a check_credential_literals.py expectation test.
run_credential_test() {
    local test_name="$1"
    local content="$2"
    local should_reject="$3" # "yes" or "no"

    echo -e "${BLUE}Test: $test_name${NC}"
    printf '%s\n' "$content" > "$TEST_DIR/cred_file.py"

    local rejected="no"
    local output
    if ! output=$(python3 scripts/ci/check_credential_literals.py "$TEST_DIR/cred_file.py" 2>&1); then
        rejected="yes"
    fi

    if [ "$rejected" != "$should_reject" ]; then
        fail "Expected reject=$should_reject, got=$rejected"
        return
    fi

    # The checker must never echo the value it rejected.
    if [ "$rejected" = "yes" ]; then
        local value
        value=$(printf '%s' "$content" | sed -n 's/.*"\([^"]*\)".*/\1/p')
        if [ -n "$value" ] && printf '%s' "$output" | grep -qF -- "$value"; then
            fail "Checker echoed the rejected value"
            return
        fi
    fi
    pass "Credential gate behaved as expected (reject=$rejected)"
}

echo -e "${YELLOW}🚨 Testing UNSAFE patterns (should be detected)${NC}"
echo "----------------------------------------"

run_test "Generic API Key" 'api_key = "super_secret_api_key_12345"' "yes"
run_test "Generic Password" 'password = "mysecretpassword123"' "yes"
run_test "API Token" 'api_token = "token_abc123def456ghi789"' "yes"
run_test "Private Key" 'private_key = "private_key_secret_value_123"' "yes"
run_test "Base64 Secret" 'secret = "cGFzc3dvcmQ9bXlfc2VjcmV0X3Bhc3N3b3Jk"' "yes"

echo ""
echo -e "${YELLOW}✅ Testing SAFE patterns (should NOT be detected)${NC}"
echo "----------------------------------------"

# `.secret-patterns.md` lists `sk-XXXXXXXXXXXXXXXX` as a safe placeholder, but a
# raw detect-secrets scan reports it as `Secret Keyword` when it sits in a
# keyword-adjacent assignment — its placeholder filters recognise
# `token-XXXX-XXXX-XXXX` and `your-api-key-here` but not this form. Documented
# under "API Keys" in .secret-patterns.md; asserted here as the real behaviour.
run_test "XXXX Placeholder (keyword-adjacent)" 'API_KEY = "sk-XXXXXXXXXXXXXXXX"' "yes"
run_test "Angle Bracket Placeholder" 'password = "<your-password>"' "no"
run_test "Token with XXXX" 'token = "token-XXXX-XXXX-XXXX"' "no"
run_test "Stars Placeholder" 'SECRET = "****"' "no"
run_test "Example Placeholder" 'key = "your-api-key-here"' "no"
run_test "Dots Placeholder" 'token = "..."' "no"

echo ""
echo -e "${YELLOW}🔑 Testing Graphistry personal-key gate${NC}"
echo "----------------------------------------"

# Assembled at runtime so this script contains no credential-shaped literal.
FAKE_ID="A1B2C3""D4E5"
FAKE_SECRET="A1B2C3D4""E5F6G7H8"
KEY_ID="personal_key_""id"
KEY_SECRET="personal_key_""secret"

run_credential_test "Key id literal" "$KEY_ID = \"$FAKE_ID\"" "yes"
run_credential_test "Key secret literal" "$KEY_SECRET = \"$FAKE_SECRET\"" "yes"
run_credential_test "Shape in unrelated variable" "blob = \"$FAKE_SECRET\"" "yes"
run_credential_test "Env default" "os.getenv(\"PERSONAL_KEY_SECRET\", \"$FAKE_SECRET\")" "yes"
run_credential_test "Angle placeholder" "$KEY_ID = \"<your-personal-key-id>\"" "no"
run_credential_test "Mock value" "$KEY_ID = \"pk_123\"" "no"

echo ""
echo -e "${YELLOW}🧪 Testing with actual scripts${NC}"
echo "----------------------------------------"

echo -e "${BLUE}Testing centralized script:${NC}"
if ./scripts/ci/secret-detection.sh > /dev/null 2>&1; then
    pass "Secret detection script runs successfully"
else
    fail "Secret detection script failed"
fi

echo -e "${BLUE}Testing pre-commit wrapper:${NC}"
if ./scripts/pre-commit-secret-check.sh > /dev/null 2>&1; then
    pass "Pre-commit wrapper runs successfully"
else
    fail "Pre-commit wrapper failed"
fi

# Summary
echo ""
echo "========================================"
echo -e "${BLUE}📊 Test Summary${NC}"
echo "----------------------------------------"
echo -e "  Passed: ${GREEN}$PASSED${NC}"
echo -e "  Failed: ${RED}$FAILED${NC}"

if [ "$FAILED" -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  Some tests failed. Review the output above.${NC}"
    exit 1
fi
