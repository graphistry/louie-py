# Broken Link Detection

This guide provides systematic steps to detect and fix broken links in the documentation.

## Quick Check (Manual)

For immediate verification during development:

### 1. Find All Markdown Links
```bash
# Find all internal markdown links
grep -r "](.*\.md)" docs/ --include="*.md"

# Find all external links
grep -r "](http" docs/ --include="*.md"
```

### 2. Verify Internal Links Exist
```bash
# Extract just the file paths and check if they exist
grep -r "](.*\.md)" docs/ --include="*.md" | \
  sed 's/.*](\([^)]*\)).*/\1/' | \
  sort -u | \
  while read link; do
    # Handle relative paths
    if [[ "$link" == ../* ]]; then
      # From docs/subfolder, ../ means docs/
      echo "Checking: docs/${link#../}"
      [ -f "docs/${link#../}" ] || echo "BROKEN: $link"
    elif [[ "$link" == */* ]]; then
      # Relative path from docs root
      echo "Checking: docs/$link"
      [ -f "docs/$link" ] || echo "BROKEN: $link"
    else
      # Same directory link
      echo "Checking: $link (same dir)"
    fi
  done
```

### 3. Check mkdocs Navigation
```bash
# Verify all nav entries exist
python3 -c "
import yaml
with open('mkdocs.yml') as f:
    config = yaml.safe_load(f)

def check_nav(nav_item, prefix=''):
    if isinstance(nav_item, dict):
        for key, value in nav_item.items():
            if isinstance(value, str):
                file_path = f'docs/{value}'
                if not os.path.exists(file_path):
                    print(f'BROKEN NAV: {key} -> {value}')
            elif isinstance(value, list):
                for item in value:
                    check_nav(item, prefix)
    elif isinstance(nav_item, str):
        file_path = f'docs/{nav_item}'
        if not os.path.exists(file_path):
            print(f'BROKEN NAV: {nav_item}')

import os
for item in config.get('nav', []):
    check_nav(item)
"
```

## Automated Solutions

### Option 1: Using markdown-link-check (Recommended)

Install and run markdown-link-check:

```bash
# Install globally
npm install -g markdown-link-check

# Check all markdown files
find docs/ -name "*.md" -exec markdown-link-check {} \;

# Check specific file
markdown-link-check docs/index.md

# With config file (optional)
markdown-link-check -c .markdown-link-check.json docs/index.md
```

Create `.markdown-link-check.json` for configuration:
```json
{
  "ignorePatterns": [
    {
      "pattern": "^http://localhost"
    }
  ],
  "replacementPatterns": [
    {
      "pattern": "^/",
      "replacement": "https://louie-py.readthedocs.io/"
    }
  ],
  "timeout": "10s",
  "retryOn429": true,
  "aliveStatusCodes": [200, 206]
}
```

### Option 2: Using linkcheck (Python)

```bash
# Install linkcheck
pip install linkcheck

# Check documentation
linkcheck docs/

# Check specific file
linkcheck docs/index.md
```

### Option 3: Using lychee (Rust-based, fast)

```bash
# Install lychee
cargo install lychee
# or: brew install lychee

# Check all markdown files
lychee docs/**/*.md

# With custom config
lychee --config lychee.toml docs/**/*.md
```

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/link-check.yml`:

```yaml
name: Link Check

on:
  push:
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
  pull_request:
    paths:
      - 'docs/**' 
      - 'mkdocs.yml'

jobs:
  markdown-link-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
        with:
          use-quiet-mode: 'yes'
          use-verbose-mode: 'yes'
          config-file: '.markdown-link-check.json'
          folder-path: 'docs'
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: markdown-link-check
        name: Markdown Link Check
        entry: markdown-link-check
        language: node
        files: \.md$
        additional_dependencies: ['markdown-link-check']
```

## Common Link Issues

### 1. Relative Path Problems
```bash
# Wrong: From docs/guides/examples.md
[link](../api/client.md)  # Should be: ../api/client.md

# Right: From docs/guides/examples.md  
[link](../api/client.md)  # Correct relative path
```

### 2. Case Sensitivity
```bash
# These are different on case-sensitive systems
[link](API/client.md)     # Wrong
[link](api/client.md)     # Right
```

### 3. Missing File Extensions
```bash
# Wrong
[link](installation)      # Missing .md

# Right  
[link](installation.md)   # Include extension
```

## Systematic Checking Process

### During Development
1. **Before committing**: Run quick manual check
2. **In PR**: Automated CI check runs
3. **Before release**: Full link validation

### Regular Maintenance
1. **Weekly**: Automated external link check
2. **Monthly**: Full documentation review
3. **On structure changes**: Complete link audit

### Emergency Fixes
1. **Identify**: Use grep to find all references to moved/deleted files
2. **Replace**: Use sed or find-replace to update links
3. **Verify**: Run full link check before committing

## Troubleshooting

### False Positives
- **Rate limiting**: Add delays or retry logic
- **Authentication required**: Add to ignore list
- **Localhost links**: Configure replacement patterns

### Performance Issues
- **Large docs**: Use parallel checking with `-P` flag
- **Slow external links**: Set reasonable timeouts
- **CI timeouts**: Split into multiple jobs

### Link Maintenance
- **Regular audits**: Schedule monthly checks
- **Version updates**: Check links when dependencies change
- **Redirects**: Update old URLs to new destinations