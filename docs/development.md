# Developer Guide

> **AI Note**: Keep this file under 500 lines for AI assistant readability

This guide covers local development workflows, tools, and conventions for contributing to the LouieAI Python client library.

## Quick Start (30 seconds)

```bash
# Clone and setup
git clone <repo-url>
cd louie-py
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
pre-commit install

# Verify setup
ruff check . && ruff format --check . && mypy . && pytest -q
```

## Local Development Environment

### Prerequisites
- **Python 3.11+** (3.12+ recommended)
- **uv package manager** (faster than pip)
- **Git** for version control
- **Graphistry account** for testing against real API

### Environment Setup
```bash
# Create virtual environment with specific Python version
uv venv --python 3.12 .venv
source .venv/bin/activate

# Install in development mode with all dev dependencies
uv pip install -e ".[dev]"

# Set up pre-commit hooks (runs on every commit)
pre-commit install
```

### Project Structure
```
src/louieai/          # Main package code
tests/               # Test suite
docs/                # Documentation source
.github/workflows/   # CI/CD configuration
pyproject.toml       # Project configuration
```

## Tool Usage

### uv (Package Manager)
```bash
# Install dependencies
uv pip install -e ".[dev]"        # Dev install with all tools
uv pip install -e ".[docs]"       # Just docs dependencies

# Update dependencies
uv pip compile --upgrade          # Update lockfile
uv pip sync requirements.txt      # Sync to lockfile

# Create fresh environment
uv venv --python 3.12 .venv-clean
```

### ruff (Linter + Formatter)
```bash
# Check code (linting)
ruff check .                      # Check all files
ruff check src/                   # Check specific directory
ruff check --fix .                # Auto-fix issues

# Format code
ruff format .                     # Format all files
ruff format --check .             # Check if formatting needed
ruff format --diff .              # Show formatting changes
```

### mypy (Type Checker)
```bash
# Type check
mypy .                           # Check all files
mypy src/louieai/                # Check specific package
mypy --no-error-summary .        # Less verbose output

# Common issues:
# - Missing imports: Add to pyproject.toml [[tool.mypy.overrides]]
# - Test files: Use ignore_errors = true for complex mocking
```

### pytest (Test Runner)
```bash
# Run tests
pytest                           # All tests
pytest -v                        # Verbose output
pytest -x                        # Stop on first failure
pytest -q                        # Quiet output

# Parallel testing (faster)
pytest -n auto                   # Use all CPU cores
pytest -n 4                      # Use 4 processes

# Specific tests
pytest tests/test_louie_client.py # Single file
pytest -k "test_error"           # Tests matching pattern
```

## CI Workflow Integration

### Local Testing (Match CI)
```bash
# Run the same checks as CI
ruff check .
ruff format --check .
mypy .
pytest -q
```

### Pre-commit Hooks
Our pre-commit configuration runs:
- `ruff check --fix` (auto-fix linting issues)
- `ruff format` (auto-format code)
- `mypy` (type checking)
- `python-check-blanket-noqa` (prevent lazy # noqa usage)

### CI Pipeline
- **Matrix**: Tests on Python 3.11, 3.12, 3.13
- **Steps**: Lint → Format → Type Check → Test
- **Triggers**: PRs and pushes to main/develop/feature/*

### Debugging CI Failures
1. **Lint failures**: Run `ruff check . --fix` locally
2. **Format failures**: Run `ruff format .` locally  
3. **Type failures**: Run `mypy .` locally, check overrides in pyproject.toml
4. **Test failures**: Run `pytest -v` locally, check for environment differences

## Development Conventions

### Code Style
- **Line length**: 88 characters (Black/Ruff standard)
- **Imports**: Organized by ruff (stdlib, third-party, local)
- **Type hints**: Required for all public functions
- **Docstrings**: Required for all public APIs

### Commit Messages
```
type: brief description

Longer explanation if needed.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`

### Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes  
- `docs/description` - Documentation changes
- `chore/description` - Maintenance tasks

### Pull Requests
- Link to relevant issues
- Include test coverage for new features
- Ensure all CI checks pass
- Update documentation if needed

## Testing Guide

### Test Organization
```python
# tests/test_louie_client.py structure:
def test_feature_success():           # Happy path
def test_feature_error_handling():    # Error conditions  
def test_feature_edge_cases():        # Boundary conditions
```

### Mocking Patterns
```python
# Mock external dependencies
def test_api_call(monkeypatch):
    monkeypatch.setattr(graphistry, "api_token", lambda: "fake-token")
    monkeypatch.setattr(httpx, "post", mock_response)
    # Test logic here
```

### Test Data
- Keep test data minimal and focused
- Use factories for complex objects
- Mock external API calls (don't hit real services in tests)

### Coverage Goals
- Aim for >90% code coverage
- Focus on critical paths and error handling
- Use `pytest --cov=louieai` to check coverage

## Troubleshooting

### Common Issues

**Import errors in tests:**
```python
# Fix: Ensure proper imports
import louieai  # Not from louieai import ...
```

**Mypy errors with external libraries:**
```toml
# Fix: Add to pyproject.toml
[[tool.mypy.overrides]]
module = "problematic_library.*"
ignore_missing_imports = true
```

**Ruff format conflicts:**
- Ruff formatter replaces Black - don't use both
- Use `ruff format` not `black`

**Pre-commit failures:**
```bash
# Skip pre-commit for emergency fixes
git commit --no-verify -m "emergency fix"

# Fix pre-commit issues
pre-commit run --all-files
```

### Environment Issues
- **Python version**: Ensure 3.11+ with `python --version`
- **Dependencies**: Fresh install with `uv pip install -e ".[dev]"`
- **Cache issues**: Clear with `rm -rf .ruff_cache .mypy_cache`

## Release Process

### Dynamic Versioning
We use **setuptools_scm** for automatic version management:
- Version is determined by git tags (no manual version files)
- Development builds show commit hash: `0.1.1.dev0+g130bd33`
- Tagged releases show clean version: `0.1.0`

### Creating Releases
1. **Update CHANGELOG.md** with changes for new version
2. **Test locally**: `ruff check . && mypy . && pytest`
3. **Commit changes**: `git commit -m "docs: update CHANGELOG for v0.1.0"`
4. **Create tag**: `git tag v0.1.0`
5. **Push tag**: `git push origin v0.1.0`
6. **CI**: GitHub Actions automatically builds and publishes to PyPI
7. **Verify**: Check PyPI and test `uv pip install louieai==0.1.0`

### Version Detection
```bash
# Check current version (includes git info if after tag)
python -c "import louieai; print(louieai.__version__)"

# Check what setuptools_scm would generate
python -c "from setuptools_scm import get_version; print(get_version())"
```

### Pre-release Checklist
- [ ] All tests pass locally and in CI
- [ ] Documentation is up to date
- [ ] CHANGELOG.md includes all changes for this version
- [ ] Tag follows semantic versioning (vX.Y.Z format)
- [ ] PyPI credentials are configured in GitHub secrets

---

For contribution workflows and community guidelines, see [CONTRIBUTING.md](https://github.com/<owner>/louieai/blob/main/CONTRIBUTING.md).