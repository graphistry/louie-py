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

# Verify setup (use smart scripts)
./scripts/ci-quick.sh
```

## Local Development Environment

### Prerequisites
- **Python 3.10+** (3.12+ recommended)
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
scripts/             # Development scripts (CI simulation)
.github/workflows/   # CI/CD configuration
pyproject.toml       # Project configuration
```

## Tool Usage

### uv (Package Manager)
```bash
# Install dependencies
uv pip install -e ".[dev]"        # Dev install with all tools
uv pip install -e ".[docs]"       # Just docs dependencies

# Run commands (project uses ./bin/uv wrapper)
./bin/uv run pytest               # Auto-manages environment
./bin/uv run ruff check .         # No activation needed
./bin/uv run mypy .               # Handles dependencies automatically

# Environment management
uv venv --python 3.12 .venv       # Create virtual environment
uv pip compile --upgrade          # Update lockfile
uv venv --python 3.12 .venv-clean # Fresh environment
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
# Run tests (always use ./bin/uv for correct environment)
./bin/uv run pytest              # All tests
./bin/uv run pytest -v           # Verbose output
./bin/uv run pytest -x           # Stop on first failure
./bin/uv run pytest -q           # Quiet output

# Or use the smart script (recommended)
./scripts/pytest.sh              # Includes coverage + threshold
./scripts/pytest.sh -v           # Your args + smart defaults

# Parallel testing (faster)
./bin/uv run pytest -n auto      # Use all CPU cores
./bin/uv run pytest -n 4         # Use 4 processes

# Specific tests
./bin/uv run pytest tests/unit/test_client.py # Single file
./bin/uv run pytest -k "test_error"    # Tests matching pattern
```

**Important Python Environment Note:**
- Always use `./bin/uv run` or our smart scripts to ensure correct Python version
- The project requires Python 3.10+ (we use 3.12 in development)
- A `.python-version` file pins the version for consistency
- If you see Python 3.8 errors, you're likely using global Python instead of venv

## Local CI Simulation

### Smart Development Scripts

We provide intelligent wrapper scripts that mirror CI exactly with sensible defaults:

```bash
# Individual tool scripts (smart defaults)
./scripts/ruff.sh                     # Default: check all files
./scripts/format.sh                   # Default: format all files  
./scripts/mypy.sh                     # Default: check all files
./scripts/pytest.sh                  # Default: coverage + 85% threshold

# CI orchestration scripts
./scripts/ci-quick.sh                 # Fast feedback (errors only + tests)
./scripts/ci-local.sh                 # Full CI pipeline locally
```

### Smart Defaults vs Custom Arguments

**No arguments = Smart defaults:**
```bash
./scripts/pytest.sh                  # Runs with coverage + threshold
./scripts/ruff.sh                     # Checks all files
```

**With arguments = Full flexibility:**
```bash
./scripts/pytest.sh -v -k specific   # Adds coverage to your args
./scripts/ruff.sh format --check     # Pass-through to ruff format --check
./scripts/pytest.sh --no-cov         # User overrides, no smart defaults added
```

### Development Workflow

**Quick iteration cycle:**
```bash
# Edit code
./scripts/ci-quick.sh                 # Fast feedback (~5 seconds)
# Continue development
```

**Before push/PR:**
```bash
./scripts/ci-local.sh                 # Full CI simulation (~30 seconds)
# Confident push
```

### Coverage Requirements

**85% threshold enforced:**
- CI fails if total coverage drops below 85%
- Local scripts use same threshold for consistency
- Check coverage: `./scripts/pytest.sh` (shows percentage)

**Coverage bypass for development:**
```bash
./scripts/pytest.sh --no-cov         # Skip coverage entirely
./scripts/pytest.sh -x               # Fail-fast without coverage reporting
```

## CI Workflow Integration

### ReadTheDocs Configuration Validation

The project includes validation for `.readthedocs.yml` to catch configuration errors before they reach ReadTheDocs:

```bash
# Test validation with known errors
./scripts/test-rtd-validation.sh
```

**How it works:**
- Downloads official RTD JSON schema from their repository
- Validates `.readthedocs.yml` against the schema using jsonschema
- Catches common errors like:
  - Invalid `build.jobs` structure (must be dict, not list)
  - Missing required fields (e.g., `version`)
  - Invalid field values

**Integrated into CI:**
- Runs in `ci-quick.sh` for fast local feedback
- Runs in `ci-local.sh` for full validation
- Runs in GitHub Actions `docs-test` job

### Local Testing (Match CI)
```bash
# Modern approach (recommended)
./scripts/ci-local.sh                 # Exact CI replication

# Manual approach (legacy)
ruff check .
ruff format --check .
mypy .
pytest -q --cov=louieai --cov-report=xml --cov-report=term --cov-fail-under=85
```

### Pre-commit Hooks
Our pre-commit configuration runs:
- `ruff check --fix` (auto-fix linting issues)
- `ruff format` (auto-format code)
- `mypy` (type checking)
- `python-check-blanket-noqa` (prevent lazy # noqa usage)

### CI Pipeline
- **Matrix**: Tests on Python 3.10, 3.11, 3.12, 3.13
- **Steps**: Lint → Format → Type Check → Test + Coverage (85% threshold)
- **Triggers**: PRs and pushes to main/develop/feature/*
- **Coverage**: XML reports generated for all runs

### Debugging CI Failures

**Use local CI simulation:**
```bash
./scripts/ci-local.sh                 # Replicate exact CI environment
```

**Individual debugging:**
1. **Lint failures**: `./scripts/ruff.sh` then `./scripts/format.sh --fix`
2. **Format failures**: `./scripts/format.sh` to auto-fix
3. **Type failures**: `./scripts/mypy.sh`, check overrides in pyproject.toml
4. **Test failures**: `./scripts/pytest.sh -v` for detailed output
5. **Coverage failures**: `./scripts/pytest.sh` shows current percentage

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
# tests/unit/test_client.py structure:
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
- Use `./scripts/pytest.sh` to check coverage

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

**Python Version Conflicts:**
```bash
# Check environment (run our diagnostic script)
./scripts/test-env-check.sh

# Common issue: global Python being used instead of venv
# Solution 1: Always use ./bin/uv run  
./bin/uv run python --version    # Should show 3.12.x
./bin/uv run pytest              # Correct way to run tests

# Solution 2: Use python -m pattern
./bin/uv run python -m pytest    # Even more explicit

# Solution 3: Reset environment if corrupted
rm -rf .venv
uv venv --python 3.12
uv pip install -e ".[dev]"
```

**Other Environment Issues:**
- **Dependencies**: Fresh install with `uv pip install -e ".[dev]"`
- **Cache issues**: Clear with `rm -rf .ruff_cache .mypy_cache`
- **Global tools interfering**: Check `which pytest` (should be in .venv)

## Release Process

### Dynamic Versioning
We use **setuptools_scm** for automatic version management:
- Version is determined by git tags (no manual version files)
- Development builds show commit hash: `0.1.1.dev0+g130bd33`
- Tagged releases show clean version: `0.1.0`

### Changelog Management
We use **dual changelog approach** for maximum compatibility:
- **CHANGELOG.md**: Portable format following [keepachangelog.com](https://keepachangelog.com/)
- **GitHub Releases**: Rich formatting with API accessibility

#### Updating CHANGELOG.md
```bash
# Add new version section (copy from [Unreleased])
## [0.2.0] - 2025-07-27

### Added
- New feature description

### Changed  
- Modified functionality

### Fixed
- Bug fix description
```

### Creating Releases
1. **Update CHANGELOG.md**:
   - Move changes from `[Unreleased]` to new version section
   - Use format: `## [X.Y.Z] - YYYY-MM-DD`
   - Organize by: Added, Changed, Deprecated, Removed, Fixed, Security

2. **Test locally**: `ruff check . && mypy . && pytest`

3. **Commit changes**: `git commit -m "docs: update CHANGELOG for vX.Y.Z"`

4. **Create tag**: `git tag vX.Y.Z`

5. **Push tag**: `git push origin vX.Y.Z`

6. **Create GitHub Release**:
   ```bash
   # Using GitHub CLI
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-from-tag
   
   # Or manually: copy CHANGELOG.md section to GitHub release notes
   ```

7. **CI**: GitHub Actions automatically builds and publishes to PyPI

8. **Verify**: Check PyPI and test `uv pip install louieai==X.Y.Z`

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