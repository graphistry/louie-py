# Version Tagging Guidelines

This project uses [PEP 440](https://www.python.org/dev/peps/pep-0440/) compliant version tags to ensure compatibility with Python packaging tools and ReadTheDocs.

## Valid Tag Formats

### Release Versions
- `v0.6.0` - Standard release
- `v1.0.0` - Major release
- `v0.6.1` - Patch release

### Pre-release Versions
- `v0.6.0a1` - Alpha release (early preview)
- `v0.6.0b1` - Beta release (feature complete, testing)
- `v0.6.0rc1` - Release candidate (final testing)

### Development Versions
- `v0.6.0.dev1` - Development release
- `v0.6.0a1.dev1` - Development release of an alpha

### Post-release Versions
- `v0.6.0.post1` - Post-release fixes

## Invalid Formats

The following formats are **NOT** PEP 440 compliant and will be rejected:

- ❌ `v0.6.0-preview` → Use `v0.6.0a1` instead
- ❌ `v0.6.0-feature` → Use `v0.6.0.dev1` instead
- ❌ `v0.6.0-beta` → Use `v0.6.0b1` instead
- ❌ `v0.6.0-rc` → Use `v0.6.0rc1` instead
- ❌ `v0.6.0-anything` → Hyphens are not allowed

## Validation

Tags are automatically validated by:

1. **GitHub Actions**: Validates tags on push to prevent invalid versions
2. **Local validation script**: `python3 scripts/validate-version-tag.py <tag>`

## Creating Tags

```bash
# Create a tag
git tag v0.6.0a1

# Validate it locally (optional)
python3 scripts/validate-version-tag.py v0.6.0a1

# Push the tag
git push origin v0.6.0a1
```

## ReadTheDocs Integration

ReadTheDocs requires PEP 440 compliant versions. When you push a valid tag:

1. ReadTheDocs automatically detects the new version
2. Builds documentation for that version
3. Makes it available at the versions page

Preview versions (alpha, beta, dev) are perfect for:
- Feature branch documentation
- Testing documentation changes
- Sharing preview documentation with stakeholders

## Troubleshooting

### "Invalid version" error on ReadTheDocs

If you see `packaging.version.InvalidVersion`, the tag is not PEP 440 compliant.

1. Delete the invalid tag:
   ```bash
   git tag -d <tag>
   git push origin :refs/tags/<tag>
   ```

2. Create a valid tag using PEP 440 format:
   ```bash
   git tag v0.6.0a1  # for alpha/preview
   git push origin v0.6.0a1
   ```

### Tag already exists

If a tag already exists, increment the number:
- `v0.6.0a1` → `v0.6.0a2`
- `v0.6.0b1` → `v0.6.0b2`