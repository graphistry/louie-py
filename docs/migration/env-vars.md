# Environment Variable Migration Guide

## Overview

Starting with LouieAI v0.2.0, we've simplified environment variable naming to use PyGraphistry's standard environment variables. This guide helps you migrate from the old `LOUIE_*` variables to the standardized `GRAPHISTRY_*` variables.

## Migration Summary

| Old Variable | New Variable | Purpose |
|--------------|--------------|---------|
| `LOUIE_USER` | `GRAPHISTRY_USERNAME` | PyGraphistry username |
| `LOUIE_PASS` | `GRAPHISTRY_PASSWORD` | PyGraphistry password |
| `LOUIE_API_KEY` | `GRAPHISTRY_API_KEY` | API key authentication |
| `LOUIE_PERSONAL_KEY_ID` | `GRAPHISTRY_PERSONAL_KEY_ID` | Personal key ID (service accounts) |
| `LOUIE_PERSONAL_KEY_SECRET` | `GRAPHISTRY_PERSONAL_KEY_SECRET` | Personal key secret |
| `LOUIE_ORG_NAME` | `GRAPHISTRY_ORG_NAME` | Organization name |
| `LOUIE_SERVER` | *Removed* | Use PyGraphistry's server parameter |
| `LOUIE_URL` | `LOUIE_URL` | *Unchanged* - Louie-specific server URL |
| N/A | `LOUIE_TIMEOUT` | *New* - Overall request timeout (default: 300s) |
| N/A | `LOUIE_STREAMING_TIMEOUT` | *New* - Streaming chunk timeout (default: 120s) |

## Quick Migration Steps

### 1. Update Shell Configuration

If you have environment variables in your shell configuration (`.bashrc`, `.zshrc`, etc.):

**Before:**
```bash
export LOUIE_USER=myusername
export LOUIE_PASS=mypassword
```

**After:**
```bash
export GRAPHISTRY_USERNAME=myusername
export GRAPHISTRY_PASSWORD=mypassword
```

### 2. Update `.env` Files

If you use `.env` files for local development:

**Before:**
```env
LOUIE_USER=myusername
LOUIE_PASS=mypassword
LOUIE_API_KEY=my_api_key
```

**After:**
```env
GRAPHISTRY_USERNAME=myusername
GRAPHISTRY_PASSWORD=mypassword
GRAPHISTRY_API_KEY=my_api_key
```

### 3. Update CI/CD Configuration

Update your CI/CD pipelines to use the new variable names:

**GitHub Actions Example:**
```yaml
# Before
env:
  LOUIE_USER: ${{ secrets.LOUIE_USER }}
  LOUIE_PASS: ${{ secrets.LOUIE_PASS }}

# After
env:
  GRAPHISTRY_USERNAME: ${{ secrets.GRAPHISTRY_USERNAME }}
  GRAPHISTRY_PASSWORD: ${{ secrets.GRAPHISTRY_PASSWORD }}
```

### 4. Update Docker Configurations

**Docker Compose Example:**
```yaml
# Before
environment:
  - LOUIE_USER=${LOUIE_USER}
  - LOUIE_PASS=${LOUIE_PASS}

# After
environment:
  - GRAPHISTRY_USERNAME=${GRAPHISTRY_USERNAME}
  - GRAPHISTRY_PASSWORD=${GRAPHISTRY_PASSWORD}
```

## Authentication Priority

The authentication system checks credentials in this order:

1. **Personal Key Authentication** (highest priority)
   - `GRAPHISTRY_PERSONAL_KEY_ID` + `GRAPHISTRY_PERSONAL_KEY_SECRET`
   
2. **API Key Authentication**
   - `GRAPHISTRY_API_KEY`
   
3. **Username/Password Authentication**
   - `GRAPHISTRY_USERNAME` + `GRAPHISTRY_PASSWORD`

## Special Cases

### Louie-Specific Configuration

Some environment variables remain Louie-specific and don't follow the `GRAPHISTRY_*` pattern:

```bash
# Louie service endpoint
export LOUIE_URL=https://custom.louie.ai

# Timeout configuration (new in v0.3.0)
export LOUIE_TIMEOUT=600  # Overall timeout in seconds (default: 300)
export LOUIE_STREAMING_TIMEOUT=180  # Per-chunk timeout in seconds (default: 120)
```

These timeout settings are useful for long-running agentic workflows.

### Server Configuration

Previously, `LOUIE_SERVER` was used to specify the PyGraphistry server. This is now handled through the PyGraphistry authentication:

**Before:**
```bash
export LOUIE_SERVER=hub.graphistry.com
```

**After:**
```python
# Specify server in code
from louieai import LouieClient
client = LouieClient(server="hub.graphistry.com")

# Or with graphistry.register()
import graphistry
graphistry.register(api=3, server="hub.graphistry.com", username="...", password="...")
```

## Backward Compatibility

For a smooth transition, the current version still checks for old `LOUIE_*` variables as a fallback, but this support will be removed in a future version. We recommend updating to the new variable names as soon as possible.

## Verification

To verify your migration is complete:

1. Unset old variables:
   ```bash
   unset LOUIE_USER LOUIE_PASS LOUIE_API_KEY LOUIE_PERSONAL_KEY_ID LOUIE_PERSONAL_KEY_SECRET
   ```

2. Test authentication with new variables:
   ```python
   from louieai.notebook import lui
   lui("Test query")  # Should authenticate successfully
   ```

## Troubleshooting

If you encounter authentication errors after migration:

1. **Check variable names**: Ensure you're using `GRAPHISTRY_*` not `LOUIE_*`
2. **Check spelling**: `GRAPHISTRY_USERNAME` not `GRAPHISTRY_USER`
3. **Verify values**: Make sure the values were copied correctly
4. **Clear old variables**: Unset any remaining `LOUIE_*` variables

## Need Help?

If you have questions about the migration:

- Check the [Authentication Guide](../guides/authentication.md)
- Open an issue on [GitHub](https://github.com/graphistry/louie-py/issues)
- Contact Graphistry support