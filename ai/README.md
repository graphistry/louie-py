# AI Assistant Guidelines

This document provides guidelines for AI assistants working on the louie-py project.

## Project Philosophy

**"Simple API, Full Power"** - The LouieAI client is intentionally minimal:
- Only 4 primary methods that access all Louie.ai capabilities
- The server handles complexity, not the client
- Natural language is the primary interface

## Critical Development Practices

### 1. Environment Management

**ALWAYS use `uv run` for Python commands:**
```bash
# ✅ Correct
uv run python script.py
uv run pytest

# ❌ Never use
python script.py
pytest
```

**Python version:** Development uses Python 3.12 (minimum 3.11+ required)

### 2. Development Workflow

**Smart scripts for different needs:**
```bash
# Fast feedback during development
./scripts/ci-quick.sh

# Full CI validation before commits
./scripts/ci-local.sh

# Individual tool usage
./scripts/ruff.sh         # Linting
./scripts/format.sh       # Code formatting
./scripts/mypy.sh         # Type checking
./scripts/pytest.sh       # Testing
```

### 3. Security Best Practices

**CRITICAL: Secret Storage Rules**

**What constitutes a secret:**
- API keys and authentication tokens
- Passwords and credentials
- Server URLs and hostnames
- Organization names
- Customer identifiers
- Any environment-specific configuration

**Storage rules:**
- **NEVER** save secrets to version-controlled directories
- **ONLY SAFE DIRECTORIES**: 
  - `tmp/` (gitignored)
  - `plans/` (gitignored)
  - `.env` files in project root (gitignored)
- **UNSAFE DIRECTORIES**: `src/`, `tests/`, `docs/`, `scripts/`, `ai/`, etc.

**Secret Detection:**
- Pre-commit hooks automatically scan for secrets
- Use clear placeholders in docs: `<your-password>`, `sk-XXXXXXXX`
- See [DEVELOP.md](../DEVELOP.md#secret-detection) for details

**Best Practice: Use .env files**
```bash
# Create secrets safely
echo "export LOUIE_API_KEY='secret'" > tmp/.env.local
echo "export GRAPHISTRY_TOKEN='token'" >> tmp/.env.local
echo "export LOUIE_SERVER='https://server.example.com'" >> tmp/.env.local
echo "export LOUIE_ORG='organization-name'" >> tmp/.env.local

# Source when needed
source tmp/.env.local
```

- Check for sensitive data before commits
- Use secure token handling patterns
- Never hardcode secrets in code or documentation
- Treat server URLs and org names with same security as passwords

### 4. Documentation Standards

- **Emphasize capabilities over limitations**
- Use mkdocstrings for API documentation
- Include practical examples in all docs
- Keep README focused on quick start

### 5. Testing Requirements

- **85% coverage threshold** (enforced in CI)
- Mock all external dependencies
- Test both success and error paths
- Integration tests require real Louie instance

### 6. Type Safety Standards

- **NO TYPE IGNORES**: Never use `# type: ignore` comments - fix the underlying issues
- **Proper Type Annotations**: All functions must have complete type annotations
- **Graphistry Types**: Use graphistry 0.41.0+ which has proper type exports
- **Strict MyPy**: Run with strict mode enabled - resolve all type errors properly

## Project Structure

```
louie-py/
├── src/louieai/          # Main package code
│   ├── client.py         # Core LouieClient implementation
│   ├── auth.py           # Authentication handling
│   └── response_types.py # Response type definitions
├── tests/                # Test suite
│   ├── unit/            # Unit tests (mocked)
│   └── integration/     # Integration tests (real API)
├── docs/                # MkDocs documentation
├── scripts/             # Development scripts
├── ai/                  # AI assistant resources
└── tmp/                 # Temporary test files (gitignored)
```

## Response Types

The client handles four main response types from Louie.ai:

1. **`DfElement`** - DataFrames returned from data queries
2. **`GraphElement`** - Graphistry visualizations
3. **`TextElement`** - Natural language responses
4. **`KeplerElement`** - Geographic/map visualizations

## Key Guidelines

### 1. Before Starting Work

- Check current branch and status
- Verify environment with `uv run python --version`
- Review recent commits for context
- Run `./scripts/ci-quick.sh` to ensure clean state

### 2. When Making Changes

- Follow existing code patterns
- Use type hints everywhere
- Write tests for new functionality
- Update documentation as needed

### 3. Code Style

- Let tools handle formatting (ruff)
- Focus on clarity and simplicity
- Avoid over-engineering
- Keep the API surface minimal

### 4. Commit Practices

- Use conventional commits (feat:, fix:, docs:, etc.)
- Make atomic, focused commits
- Write clear commit messages
- Reference issues when applicable

### 5. PR Guidelines

- Run full CI locally first
- Include tests for all changes
- Update documentation
- Keep PRs focused and reviewable

## Common Tasks

### Running Tests
```bash
# All tests with coverage
./scripts/pytest.sh

# Specific test file
./scripts/pytest.sh tests/unit/test_client.py

# Integration tests (needs credentials)
./scripts/pytest.sh tests/integration/
```

### Checking Code Quality
```bash
# Full CI suite
./scripts/ci-local.sh

# Individual checks
./scripts/ruff.sh check
./scripts/format.sh --check
./scripts/mypy.sh
```

### Building Documentation
```bash
# Install docs dependencies
uv pip install -e ".[docs]"

# Build and serve locally
uv run mkdocs serve

# Build static site
uv run mkdocs build
```

## Integration with Graphistry

The client relies on PyGraphistry for authentication:

```python
import graphistry
from louieai import LouieClient

# Authenticate first
graphistry.register(api=3, username="user", password="pass")

# Client uses the same session
client = LouieClient()
```

## Error Handling Philosophy

- Provide detailed, actionable error messages
- Include HTTP status codes and response content
- Guide users toward solutions
- Never hide or swallow exceptions

## Future Considerations

When adding features, consider:

1. Does this maintain the "simple API" philosophy?
2. Should complexity live in the server or client?
3. Is this solving a real user need?
4. Will this break backward compatibility?

## Quick Reference

### Essential Commands
```bash
# Development cycle
./scripts/ci-quick.sh    # Fast checks
./scripts/ci-local.sh    # Full validation
git add -p              # Stage changes
git commit -m "..."     # Commit
git push                # Push to remote
```

### File Locations
- Client code: `src/louieai/client.py`
- Tests: `tests/unit/` and `tests/integration/`
- Docs: `docs/` (MkDocs format)
- Scripts: `scripts/` (all executable)

### Key Dependencies
- `graphistry>=0.41.0` - Authentication and graph handling
- `httpx>=0.28.0` - HTTP client
- `pandas>=2.0.0` - Data manipulation
- `pyarrow>=21.0.0` - Data serialization

Remember: Keep it simple, make it work, then make it better.