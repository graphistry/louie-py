# Link Checking Guide

Check for broken links in the documentation using our built-in script.

## Quick Check

```bash
# Run the link checker
./scripts/check-links.sh
```

This script automatically:
- Checks all internal markdown links in `docs/`
- Validates mkdocs navigation entries
- Reports broken links with their locations

## What the Script Does

1. **Internal Links**: Finds all markdown link patterns and verifies the target files exist
2. **Navigation**: Validates all entries in `mkdocs.yml` point to existing files
3. **Summary**: Reports total broken links and provides fix suggestions

## Common Issues

### Relative Path Problems
```markdown
<!-- Wrong: From docs/guides/examples.md -->
[link](client.md)         <!-- File not in same directory -->

<!-- Right -->
[link](../api/client.md)  <!-- Correct relative path -->
```

### Case Sensitivity
```markdown
<!-- Wrong -->
[link](API/Client.md)     <!-- Wrong case -->

<!-- Right -->
[link](api/client.md)     <!-- Correct case -->
```

### Missing Extensions
```markdown
<!-- Wrong -->
[link](index)             <!-- Missing .md -->

<!-- Right -->
[link](index.md)          <!-- Include extension -->
```

## CI Integration

The link checker runs automatically in CI on:
- Pull requests that modify docs
- Commits to main branch

## Advanced Checking

For external link validation or more detailed analysis:

```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check all files including external links
find docs/ -name "*.md" -exec markdown-link-check {} \;
```

## Fixing Broken Links

1. Run `./scripts/check-links.sh` to identify issues
2. Update the link paths in source files
3. Create missing files if needed
4. Update mkdocs.yml if navigation changed
5. Run the script again to verify fixes