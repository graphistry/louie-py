# API Reference

This section contains the complete API reference for the LouieAI Python client library.

## Overview

LouieAI provides two APIs for interacting with the Louie.ai service:

### Notebook API (Recommended for Jupyter)

```python
from louieai.notebook import lui

# Ask questions naturally
lui("Show me patterns in my data")
print(lui.text)
df = lui.df
```

### Traditional Client API

```python
import louieai
import graphistry

# Authenticate with Graphistry
graphistry.register(api=3, username="your_user", password="your_pass")

# Create client and ask questions
client = louieai.LouieClient()
response = client.add_cell("", "Show me patterns in my data")
```

## Main Components

### [Notebook API](notebook.md)

Streamlined interface optimized for Jupyter notebooks with implicit thread management and easy data access.

### [LouieClient](client.md)

The traditional client class for interacting with Louie.ai. Provides full control over threads, authentication, and responses.

## Installation

Using uv (recommended):
```bash
uv pip install louieai
```

Using pip:
```bash
pip install louieai
```

## Requirements

- Python 3.8 or higher
- Active Graphistry account with API access
- Network access to Louie.ai service

## Authentication

Both APIs support multiple authentication methods:

1. **Environment Variables** (recommended for notebooks):
   ```bash
   export LOUIE_USER=your_username
   export LOUIE_PASS=your_password
   ```

2. **Graphistry Registration**:
   ```python
   import graphistry
   graphistry.register(api=3, username="user", password="pass")
   ```

3. **Direct Credentials**:
   ```python
   client = louieai.LouieClient(username="user", password="pass")
   ```

## Error Handling

- **Notebook API**: Returns `None` or empty collections instead of raising exceptions
- **Client API**: Raises `RuntimeError` exceptions on failure

See the respective documentation for detailed error handling examples:
- [Notebook API Error Handling](notebook.md#error-handling)
- [Client API Error Handling](client.md#error-handling)