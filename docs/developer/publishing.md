# Publishing Guide

This guide covers how to publish new releases of the LouieAI Python client to PyPI.

## Prerequisites

- You must have maintainer access to the GitHub repository
- PyPI publishing is automated via GitHub Actions using trusted publishing

## Publishing Process

### 1. Prepare the Release

1. Ensure all changes are merged to `main`
2. Run full CI locally to verify everything passes:
   ```bash
   ./scripts/ci-local.sh
   ```

3. Update the changelog:
   - Add a new version section with the date
   - Move items from "Unreleased" to the new version
   - Follow semantic versioning guidelines

4. Commit changelog updates:
   ```bash
   git add CHANGELOG.md
   git commit -m "docs: update changelog for vX.Y.Z"
   git push
   ```

### 2. Create a GitHub Release

1. Go to the [Releases page](https://github.com/<owner>/louieai/releases)
2. Click "Draft a new release"
3. Create a new tag (e.g., `v0.1.0`) targeting `main`
4. Set the release title to the version (e.g., `v0.1.0`)
5. Copy the relevant section from CHANGELOG.md into the release description
6. Click "Publish release"

### 3. Automated Publishing

Once the release is published:

1. The `publish.yml` workflow automatically triggers
2. It builds the package using `setuptools_scm` (version from git tag)
3. Publishes to PyPI using trusted publishing (no tokens needed)
4. You can monitor progress in the [Actions tab](https://github.com/<owner>/louieai/actions)

### 4. Verify the Release

After successful publishing:

```bash
# Install from PyPI
pip install louieai==X.Y.Z

# Verify the version
python -c "import louieai; print(louieai.__version__)"
```

## Manual Publishing (Emergency Only)

If automated publishing fails, you can publish manually:

```bash
# Ensure you have the latest code
git checkout main
git pull
git checkout vX.Y.Z  # The release tag

# Clean any previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

# Upload to PyPI (requires PyPI token)
python -m twine upload dist/*
```

## Version Management

This project uses `setuptools_scm` for automatic version management:

- Version is derived from git tags
- Development builds include commit info (e.g., `0.1.0.dev5+g1234567`)
- Tagged releases have clean versions (e.g., `0.1.0`)

To check what version would be generated:

```bash
python -c "from setuptools_scm import get_version; print(get_version())"
```

## Troubleshooting

### Build Failures

If the build fails:

1. Check that all tests pass locally
2. Ensure `pyproject.toml` is valid
3. Verify git tags are properly formatted (`vX.Y.Z`)

### Publishing Failures

If publishing fails:

1. Check the GitHub Actions logs for errors
2. Verify the package name isn't taken on PyPI
3. Ensure trusted publishing is configured (repository settings)

### Version Conflicts

If you get version conflicts:

1. Ensure the tag doesn't already exist
2. Check PyPI for existing versions
3. Use a higher version number

## Post-Release Tasks

After a successful release:

1. Update any dependent projects
2. Announce the release (if applicable)
3. Close related issues and PRs
4. Start planning the next release

## Security Notes

- Never commit PyPI tokens to the repository
- Use GitHub's trusted publishing feature (configured)
- Keep release branches protected
- Sign tags with GPG if possible:
  ```bash
  git tag -s vX.Y.Z -m "Release vX.Y.Z"
  ```