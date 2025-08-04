# Notebook Utilities

This directory contains helper scripts for managing Jupyter notebooks in CI/CD pipelines.

## Scripts

### validate-notebook.py

Validates a Jupyter notebook for proper execution and security issues.

**Features:**
- Checks if notebook has been executed (has outputs)
- Detects execution errors in cells
- Scans for leaked secrets in outputs (API keys, passwords, etc.)

**Usage:**
```bash
python3 validate-notebook.py path/to/notebook.ipynb
```

**Exit codes:**
- 0: Validation passed
- 1: Validation failed (secrets found or file not found)

### clean-notebook-outputs.py

Removes outputs containing sensitive information from executed notebooks.

**Features:**
- Scans all code cell outputs for secret patterns
- Removes outputs containing sensitive data
- Preserves non-sensitive outputs
- Supports dry-run mode to preview changes

**Usage:**
```bash
# Clean sensitive outputs
python3 clean-notebook-outputs.py path/to/notebook.ipynb

# Preview what would be cleaned (dry run)
python3 clean-notebook-outputs.py path/to/notebook.ipynb --dry-run
```

## Secret Patterns Detected

Both scripts detect the following patterns:
- Personal API keys (pk_*, sk_*)
- Variable assignments with credentials
- FILL_ME_IN placeholders
- Password and secret assignments
- getpass prompts

## Integration with build-notebook.sh

These scripts are automatically used by `scripts/build-notebook.sh` to:
1. Execute notebooks with environment variables
2. Clean sensitive outputs after execution
3. Validate the final result

## Adding New Patterns

To add new secret patterns, update the `secret_patterns` list in both scripts.