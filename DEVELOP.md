# Developer Guide

This guide covers the technical setup and development workflow for contributors to the LouieAI Python client library.

## Environment Setup

### Prerequisites

- Python 3.10 or higher (3.12+ recommended)
- Git
- uv package manager (recommended) or pip

### Initial Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/louie-py.git
   cd louie-py
   ```

2. **Create virtual environment**:
   ```bash
   uv venv
   # or: python -m venv .venv
   ```

3. **Install development dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   # or: pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Environment Variables

For integration testing, create a `.env` file:

```bash
GRAPHISTRY_USERNAME=your_username
GRAPHISTRY_PASSWORD=your_password
# or
GRAPHISTRY_API_KEY=your_api_key
# or for service accounts
GRAPHISTRY_PERSONAL_KEY_ID=pk_123...
GRAPHISTRY_PERSONAL_KEY_SECRET=sk_123...
```

## Project Structure

```
louie-py/
├── src/louieai/          # Main package source
│   ├── __init__.py       # Package exports and version
│   ├── client.py         # Main LouieClient class
│   └── auth.py           # Authentication management
├── tests/
│   ├── unit/             # Unit tests (no external deps)
│   └── integration/      # Integration tests (require auth)
├── docs/                 # Documentation source
├── scripts/              # Development scripts
└── ai/                   # AI assistant templates
```

## Development Workflow

### Git Workflow

We use gitflow:
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `release/*`: Release preparation

### Creating a Feature

1. Create feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and test locally

3. Commit with sign-off:
   ```bash
   git commit -s -m "feat: add new feature"
   ```

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `test:` Test changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

## Testing

### Running Tests

**Important**: Always use `./scripts/pytest.sh` instead of `pytest` directly to ensure the correct Python version is used.

```bash
# All tests (recommended way)
./scripts/pytest.sh

# Unit tests only
./scripts/pytest.sh tests/unit/

# Integration tests (requires credentials)
./scripts/pytest.sh tests/integration/

# With coverage
./scripts/pytest.sh --cov=louieai --cov-report=term

# Alternative if scripts not available
uv run python -m pytest
```

**Note**: Running `pytest` directly may use the wrong Python version. The project requires Python 3.10+.

### Quick CI Checks

```bash
# Fast feedback during development
./scripts/ci-quick.sh

# Full CI pipeline locally
./scripts/ci-local.sh
```

### Secret Detection

The project uses `detect-secrets` to prevent accidental commits of sensitive information:

```bash
# Scan for secrets (happens automatically on commit)
./scripts/secrets.sh
# Or: uv run detect-secrets scan

# Update baseline after legitimate changes  
./scripts/secrets.sh --update-baseline
# Or: uv run detect-secrets scan --baseline .secrets.baseline

# Test secret detection system
./scripts/test-secret-detection.sh

# Audit baseline interactively
uv run detect-secrets audit .secrets.baseline
```

**Handling false positives:**
- Use clear placeholders: `<your-password>`, `sk-XXXXXXXX`, `****`
- Add inline comment: `# pragma: allowlist secret`
- See `.secret-patterns.md` for acceptable placeholder patterns

### Writing Tests

- Unit tests: Mock all external dependencies
- Integration tests: Use real API (mark with `@pytest.mark.integration`)
- Documentation tests: Automatically extracted from markdown

Example unit test:
```python
def test_client_creation():
    with patch('louieai.client.AuthManager') as mock_auth:
        client = LouieClient()
        assert client is not None
        mock_auth.assert_called_once()
```

## Code Quality

### Linting and Formatting

```bash
# Check and auto-fix issues
./scripts/ruff.sh

# Check only
ruff check .

# Format code
ruff format .
```

### Type Checking

```bash
# Run mypy
./scripts/mypy.sh

# With specific file
mypy src/louieai/client.py
```

### Pre-commit Hooks

Pre-commit runs automatically on `git commit`. To run manually:
```bash
pre-commit run --all-files
```

## Documentation

### Building Docs

```bash
# Serve locally
mkdocs serve

# Build for production
mkdocs build --strict
```

### Writing Docs

- User guides: `docs/` directory
- API docs: Docstrings in source (auto-generated)
- Examples: Include working code with test coverage

## Debugging

### Common Issues

**Import errors**: Ensure you've installed in editable mode (`-e`)

**Authentication failures**: Check `.env` file and credentials

**Type errors**: Run `mypy` to catch type issues early

### Logging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Release Process

1. Update version in `src/louieai/__init__.py`
2. Update CHANGELOG.md
3. Create release PR
4. Tag release: `git tag -s v0.1.0`
5. Push tag to trigger release workflow

## CI/CD

GitHub Actions runs on all PRs:
- Python 3.10-3.13 compatibility
- Linting and formatting checks
- Type checking
- Unit and integration tests
- Documentation building

## AI-Assisted Development

We use AI assistants for development. See `ai/templates/PLAN.md` for our planning template. This is optional but helps maintain consistency.

## Additional Resources

- [Architecture Decision Records](docs/adr/)
- [API Design Principles](docs/api-design.md)
- [Performance Guidelines](docs/performance.md)

## Getting Help

- Check existing issues
- Ask in discussions
- Review test examples
- Contact maintainers

Remember: When in doubt, look at existing code patterns and tests for guidance.