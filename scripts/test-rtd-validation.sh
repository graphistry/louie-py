#!/bin/bash
# Test the ReadTheDocs validation script with various configurations

set -e

echo "Testing ReadTheDocs validation script..."

# Save original config
cp .readthedocs.yml .readthedocs.yml.bak

# Test 1: Valid config (current)
echo -e "\n1. Testing current valid config..."
./scripts/validate-readthedocs.sh
echo "✅ Valid config test passed"

# Test 2: Invalid build.jobs (common error - should be dict not list)
echo -e "\n2. Testing invalid build.jobs config..."
cat > .readthedocs.yml << 'EOF'
version: 2
build:
  os: ubuntu-22.04
  tools:
    python: "3.11"
  jobs:
    - echo "This is wrong - should be dict not list"
mkdocs:
  configuration: mkdocs.yml
python:
  install:
    - requirements: requirements-docs.txt
EOF

if ./scripts/validate-readthedocs.sh 2>&1 | grep -q "Validation error"; then
    echo "✅ Correctly detected invalid build.jobs"
else
    echo "❌ Failed to detect invalid build.jobs"
fi

# Test 3: Missing version field
echo -e "\n3. Testing missing version field..."
cat > .readthedocs.yml << 'EOF'
build:
  os: ubuntu-22.04
  tools:
    python: "3.11"
mkdocs:
  configuration: mkdocs.yml
EOF

if ./scripts/validate-readthedocs.sh 2>&1 | grep -q "Validation error"; then
    echo "✅ Correctly detected missing version"
else
    echo "❌ Failed to detect missing version"
fi

# Restore original config
mv .readthedocs.yml.bak .readthedocs.yml
echo -e "\nAll validation tests completed!"