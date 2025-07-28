#!/bin/bash
# Validate .readthedocs.yml against the official schema

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Validating .readthedocs.yml configuration..."

# Download the official ReadTheDocs schema
echo "Downloading ReadTheDocs schema..."
curl -sSL https://raw.githubusercontent.com/readthedocs/readthedocs.org/main/readthedocs/rtd_tests/fixtures/spec/v2/schema.json -o /tmp/rtd-schema.json

# Validate using Python
uv run python -c "
import yaml
import json
import jsonschema
import sys

try:
    # Load the config
    with open('.readthedocs.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Load the schema
    with open('/tmp/rtd-schema.json', 'r') as f:
        schema = json.load(f)
    
    # Validate
    jsonschema.validate(config, schema)
    print('✅ .readthedocs.yml is valid!')
    sys.exit(0)
except jsonschema.ValidationError as e:
    print(f'❌ Validation error: {e.message}')
    print(f'   Path: {\".\" if e.path else \"root\"}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

# Cleanup
rm -f /tmp/rtd-schema.json