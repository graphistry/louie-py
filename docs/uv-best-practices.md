# UV Best Practices for louie-py

This document outlines best practices for using `uv` in the louie-py project to ensure consistent Python environments and avoid common pitfalls.

## Core Principles

1. **Always use `uv run`** - Never run Python tools directly
2. **Use `python -m` pattern** - More explicit and reliable
3. **Pin Python version** - Use `.python-version` file
4. **Check prerequisites** - Verify uv and project root
5. **Balance DRY with clarity** - Don't over-abstract

## Common Patterns

### Running Python Tools

```bash
# ❌ Bad: Direct execution (may use wrong Python)
pytest
mypy .
ruff check .

# ✅ Good: Use uv run
uv run pytest
uv run mypy .
uv run ruff check .

# ✅ Better: Use python -m pattern for Python tools
uv run python -m pytest
uv run python -m mypy .
```

### Script Structure

Every script should follow this pattern:

```bash
#!/bin/bash
# script-name.sh - Brief description
# Usage: ./scripts/script-name.sh [args...]

# Source common utilities
source "$(dirname "$0")/common.sh"

# Check prerequisites
check_uv
check_project_root

# Script logic here
```

### Environment Checks

Before running commands, verify the environment:

```bash
# Check Python version
uv run python --version  # Should show 3.12.x

# Check tool is in venv
uv run which pytest      # Should be in .venv/bin/

# Run diagnostic script
./scripts/test-env-check.sh
```

## Common Pitfalls and Solutions

### Pitfall 1: Global Python Interference

**Problem**: Global Python/tools in PATH override venv

**Solution**: 
- Use `uv run python -m tool` pattern
- Add `.python-version` file
- Check with `which python` vs `uv run which python`

### Pitfall 2: Inconsistent Environments

**Problem**: Different Python versions across environments

**Solution**:
- Pin version in `.python-version`
- Use `uv venv --python 3.12` explicitly
- Document required version in pyproject.toml

### Pitfall 3: Missing Dependencies

**Problem**: Tools not installed in venv

**Solution**:
```bash
# Install all dev dependencies
uv pip install -e ".[dev]"

# Or use uv sync for lock file
uv sync
```

## DRY (Don't Repeat Yourself) Guidelines

### When to Abstract

✅ **DO Abstract**:
- Color constants and print functions
- Environment checks (uv, project root)
- Common error handling patterns

❌ **DON'T Abstract**:
- Tool-specific default arguments
- Script-specific messages
- Simple one-liners that are clearer inline

### Shared Utilities

Use `scripts/common.sh` for truly common functionality:

```bash
# Source at top of scripts
source "$(dirname "$0")/common.sh"

# Available functions:
check_uv              # Verify uv is installed
check_project_root    # Verify in project directory
print_step           # Yellow header output
print_success        # Green success message
print_error          # Red error and exit
setup_temp_dir       # Create temp dir with cleanup
```

## Script Development Checklist

When creating new scripts:

- [ ] Start with shebang: `#!/bin/bash`
- [ ] Add header comment with description and usage
- [ ] Source `common.sh` for shared utilities
- [ ] Check prerequisites (uv, project root)
- [ ] Use `uv run` for all Python/tool execution
- [ ] Prefer `python -m` pattern for Python tools
- [ ] Add error handling with `set -e` or explicit checks
- [ ] Make executable: `chmod +x scripts/script-name.sh`
- [ ] Test in clean environment
- [ ] Document in this guide if introducing new patterns

## Testing Scripts

### Quick Test
```bash
# Run diagnostic
./scripts/test-env-check.sh

# Test specific script
./scripts/pytest.sh -v
```

### Full Test
```bash
# Reset environment
rm -rf .venv
uv venv --python 3.12
uv sync

# Run CI simulation
./scripts/ci-local.sh
```

## Debugging Environment Issues

If you encounter Python version errors:

1. **Check current environment**:
   ```bash
   ./scripts/test-env-check.sh
   ```

2. **Verify uv is using correct Python**:
   ```bash
   uv run python --version
   uv run which python
   ```

3. **Reset if needed**:
   ```bash
   rm -rf .venv
   uv venv --python 3.12
   uv sync
   ```

4. **Check for global tool interference**:
   ```bash
   which pytest  # Should NOT be in conda/system
   uv run which pytest  # Should be in .venv
   ```

## Examples

### Good Script Example

```bash
#!/bin/bash
# example.sh - Example following best practices

# Source common utilities
source "$(dirname "$0")/common.sh"

# Check prerequisites
check_uv
check_project_root

# Use python -m pattern
print_step "Running example"
uv run python -m mymodule "$@" || print_error "Example failed"
print_success "Example completed"
```

### Bad Script Example

```bash
#!/bin/bash
# ❌ Missing source common.sh
# ❌ No environment checks
# ❌ Direct tool execution

pytest  # ❌ May use wrong pytest
python script.py  # ❌ May use wrong Python
```

Remember: The goal is consistency and reliability, not perfection. When in doubt, be explicit rather than clever.