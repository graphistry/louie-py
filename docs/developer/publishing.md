# Publishing Guide

How to publish new releases of the LouieAI Python client to PyPI.

## Quick Release Process

1. **Prepare**: Ensure all changes are merged to `main` and CI passes locally (`./scripts/ci-local.sh`)
2. **Update CHANGELOG.md**: Move items from "Unreleased" to new version section
3. **Commit**: `git commit -m "docs: update changelog for vX.Y.Z"`
4. **Tag & Release**: Create GitHub release with tag `vX.Y.Z`
5. **Automated**: GitHub Actions publishes to PyPI automatically

## Detailed Steps

### 1. Create GitHub Release

1. Go to [Releases page](https://github.com/<owner>/louieai/releases)
2. Click "Draft a new release"  
3. Create tag `vX.Y.Z` targeting `main`
4. Copy CHANGELOG.md section as release description
5. Click "Publish release"

### 2. Automated Publishing

The `publish.yml` workflow:
- Tests on TestPyPI first, then publishes to PyPI
- Uses `setuptools_scm` for versioning (from git tags)
- Uses trusted publishing (no manual tokens)

### 3. Verify Release

```bash
pip install louieai==X.Y.Z
python -c "import louieai; print(louieai.__version__)"
```

## Version Management

Uses `setuptools_scm` for automatic versioning:
- Version derived from git tags (no manual version files)
- Development: `0.1.0.dev5+g1234567` 
- Releases: `0.1.0`

Check version: `python -c "from setuptools_scm import get_version; print(get_version())"`

## Emergency Manual Publishing

```bash
git checkout vX.Y.Z
rm -rf dist/ build/ *.egg-info
python -m build
python -m twine upload dist/*  # Requires PyPI token
```

## Troubleshooting

**Build failures**: Check tests pass locally, verify `pyproject.toml` and tag format (`vX.Y.Z`)

**Publishing failures**: Check GitHub Actions logs, verify trusted publishing configured

**Version conflicts**: Ensure tag doesn't exist, check PyPI, use higher version