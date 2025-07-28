# AI Assistant Guidelines for louie-py

This directory contains AI-assisted development documentation and guidelines for the louie-py project.

## Quick Start for AI Assistants

### Project Philosophy
- **"Simple API, Full Power"** - 4 methods access all Louie.ai capabilities
- Minimal client is intentional - server does the heavy lifting
- Natural language is the interface

### Critical Commands
```bash
# Always use uv run (never direct Python)
uv run pytest
uv run python -m mypy .

# Use smart scripts for development
./scripts/ci-quick.sh    # Fast feedback
./scripts/ci-local.sh    # Full CI check
```

### Key Guidelines

1. **Environment Management**
   - Always use `uv run` prefix
   - Python 3.12 for development (3.11+ required)
   - Check with `./scripts/test-env-check.sh`

2. **Security**
   - NEVER commit credentials
   - Use .env files for test credentials
   - Integration tests skip without credentials

3. **Documentation**
   - Emphasize capabilities, not limitations
   - Show complex queries with simple API
   - Use mkdocstrings for API docs

4. **Testing**
   - 85% coverage threshold
   - Mock external dependencies
   - Test both success and error paths

## Project Structure

```
src/louieai/          # Minimal client (4 methods)
tests/                # Unit and integration tests
docs/                 # User documentation
scripts/              # Development automation
plans/                # Planning documents
```

## Common Tasks

### Before Any Work
```bash
# Verify environment
./scripts/test-env-check.sh

# Quick CI check
./scripts/ci-quick.sh
```

### Adding Features
1. Update tests first
2. Implement feature
3. Update docs
4. Run `./scripts/ci-local.sh`
5. Update CHANGELOG.md

### Debugging Issues
- Python version conflicts? Check global vs venv
- Import errors? Run `uv sync`
- Test failures? Use `uv run python -m pytest -v`

## Response Types

The client handles various response types from Louie.ai:
- `DfElement` - DataFrames from queries
- `GraphElement` - Graphistry visualizations
- `TextElement` - Natural language responses
- `KeplerElement` - Geographic visualizations
- See `docs/api/response-types.md` for details

## Development Workflow

1. **Planning**: See `plans/` directory for structured planning
2. **Implementation**: Follow TDD, use type hints
3. **Documentation**: Update relevant docs
4. **Testing**: Run full CI before committing
5. **Review**: Check coverage, linting, types

## Key Files Reference

- `pyproject.toml` - Project configuration
- `.python-version` - Python version pin (3.12)
- `scripts/common.sh` - Shared utilities
- `docs/uv-best-practices.md` - UV usage guide
- `docs/query-patterns.md` - Example queries
- `plans/init/` - Detailed planning documents

## AI-Specific Tips

1. **Read the plan first** - Check `plans/init/plan-phase-3b.md`
2. **Use smart scripts** - Don't reinvent the wheel
3. **Test incrementally** - Use `./scripts/ci-quick.sh`
4. **Document as you go** - Update plans with results
5. **Ask about credentials** - Never hardcode them

Remember: This is a minimal client by design. The sophistication is in Louie.ai server, not the client.