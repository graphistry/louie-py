#!/bin/bash
# Simple broken link detection for louie-py documentation

set -e

echo "🔍 Checking documentation links..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BROKEN_COUNT=0

echo "1. Checking internal markdown links..."
echo "-------------------------------------"

# Find all internal markdown links and check if files exist
while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    link=$(echo "$line" | sed 's/.*](\([^)]*\.md\)).*/\1/')
    
    # Skip if not a markdown link
    [[ "$link" == *".md"* ]] || continue
    
    # Determine the directory of the source file
    dir=$(dirname "$file")
    
    # Resolve relative path
    if [[ "$link" == ../* ]]; then
        # Go up one directory from current file's directory
        target_file="$(cd "$dir/.." && pwd)/${link#../}"
    elif [[ "$link" == */* ]] && [[ "$link" != ../* ]]; then
        # Relative path from docs root
        target_file="docs/$link"
    else
        # Same directory
        target_file="$dir/$link"
    fi
    
    # Check if target file exists
    if [ ! -f "$target_file" ]; then
        echo -e "${RED}BROKEN${NC}: $file -> $link (resolved to: $target_file)"
        ((BROKEN_COUNT++))
    fi
done < <(grep -r "](.*\.md)" docs/ --include="*.md" 2>/dev/null || true)

echo ""
echo "2. Checking mkdocs navigation..."
echo "-------------------------------"

# Check mkdocs.yml navigation entries
python3 -c "
import yaml
import os
import sys

try:
    with open('mkdocs.yml') as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f'Error reading mkdocs.yml: {e}')
    sys.exit(1)

broken_nav = 0

def check_nav_item(item, path=''):
    global broken_nav
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str):
                file_path = f'docs/{value}'
                if not os.path.exists(file_path):
                    print(f'BROKEN NAV: {key} -> {value}')
                    broken_nav += 1
            elif isinstance(value, list):
                for subitem in value:
                    check_nav_item(subitem, path)
    elif isinstance(item, str):
        file_path = f'docs/{item}'
        if not os.path.exists(file_path):
            print(f'BROKEN NAV: {item}')
            broken_nav += 1

nav = config.get('nav', [])
for item in nav:
    check_nav_item(item)

if broken_nav == 0:
    print('✅ All navigation links are valid')
else:
    print(f'❌ Found {broken_nav} broken navigation links')
    
sys.exit(broken_nav)
" 2>/dev/null || ((BROKEN_COUNT++))

echo ""
echo "3. Summary"
echo "----------"

if [ $BROKEN_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ No broken links found!${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $BROKEN_COUNT broken link(s)${NC}"
    echo ""
    echo "To fix broken links:"
    echo "1. Update the link paths in the source files"
    echo "2. Create missing files if needed"
    echo "3. Update mkdocs.yml navigation if necessary"
    echo ""
    echo "For more detailed link checking, see docs/developer/link-checking.md"
    exit 1
fi