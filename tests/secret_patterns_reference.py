"""
Reference file for secret detection patterns - NOT A TEST FILE.

This file is NOT executed during pytest runs (doesn't match test_*.py pattern).
It intentionally contains various secret-like patterns as a reference for testing
the secret detection system. All secrets here are fake documentation examples.

To test secret detection:
  ./scripts/test-secret-detection.sh

Or manually test this file:
  uv run detect-secrets scan tests/secret_patterns_reference.py

This file is only scanned when:
  - Running manual tests with ./scripts/test-secret-detection.sh
  - Changes to secret detection files trigger the CI workflow
"""

# ============================================================================
# SAFE PATTERNS - These should NOT trigger detection
# ============================================================================

# Clear placeholders with XXXX
SAFE_API_KEY_1 = "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
SAFE_API_KEY_2 = "api-key-XXXX-XXXX-XXXX-XXXX"
SAFE_TOKEN = "token-XXXXXXXX"
SAFE_PASSWORD_MASKED = "XXXXXXXXXXXX"

# Angle bracket placeholders
SAFE_PASSWORD_PLACEHOLDER = "<your-password>"
SAFE_API_KEY_PLACEHOLDER = "<your-api-key>"
SAFE_TOKEN_PLACEHOLDER = "<your-token-here>"
SAFE_SECRET_PLACEHOLDER = "<insert-secret>"

# Other safe patterns
SAFE_DOTS = "..."
SAFE_STARS = "****"
SAFE_STARS_LONG = "**********"
SAFE_EXAMPLE = "your-api-key-here"
SAFE_EXAMPLE_2 = "replace-with-your-token"
SAFE_TODO = "TODO: add real token"

# ============================================================================
# UNSAFE PATTERNS - These SHOULD trigger detection (and be in baseline)
# These are intentionally fake/example secrets for documentation
# ============================================================================

# Common documentation examples (should be in baseline)
EXAMPLE_PASSWORD = "password123"
EXAMPLE_SECRET = "secretpassword"
DEMO_KEY = "demo-key-12345"
TEST_TOKEN = "test-token-abc123"

# Example API keys for documentation (should be in baseline)
FAKE_AWS_KEY = "AKIA_FAKE_KEY_FOR_TESTING"
FAKE_GITHUB_TOKEN = "fake_github_token_xxxxxxxxxx"
FAKE_API_KEY = "api_key_1234567890abcdef"

# ============================================================================
# TESTING INSTRUCTIONS
# ============================================================================
"""
How to test secret detection:

1. Run the test script:
   ./scripts/test-secret-detection.sh

2. Test manually:
   # Check if this file triggers detection
   uv run detect-secrets scan tests/secret_patterns_reference.py

   # Check against baseline
   uv run detect-secrets scan --baseline .secrets.baseline \
       tests/secret_patterns_reference.py

3. Update baseline if needed (when adding new example patterns):
   ./scripts/secrets.sh --update-baseline

4. CI tests run automatically when you change secret detection files:
   # See .github/workflows/secret-detection-test.yml
   # Only runs on PRs that modify secret detection files

5. Test CI script:
   ./scripts/ci/secret-detection.sh
"""

# ============================================================================
# PATTERN REFERENCE
# ============================================================================
PATTERN_GUIDE = """
SAFE PATTERNS (won't trigger):
- sk-XXXXXXXX... (X's for redaction)
- <your-password> (angle brackets)
- **** (stars for masking)
- ... (dots)
- your-key-here (obvious placeholders)

UNSAFE PATTERNS (will trigger):
- Real-looking passwords
- Base64 encoded strings
- UUID-like tokens
- API keys with real-looking patterns
"""
