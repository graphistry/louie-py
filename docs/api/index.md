# API Reference

This section contains the complete API reference for the LouieAI Python client library.

## Overview

LouieAI provides flexible APIs for interacting with the Louie.ai service:

### 1. Notebook API (Recommended for Jupyter)

```python
from louieai.notebook import lui

# Ask questions naturally
lui("Show me patterns in my data")
print(lui.text)
df = lui.df
```

### 2. Factory Function (New in v0.2.0)

```python
from louieai import louie

# Create callable interface with various auth methods
lui = louie()  # Uses environment variables
lui = louie(username="user", password="pass")  # Direct auth
lui = louie(graphistry_client)  # From PyGraphistry

# Use it naturally
lui("Analyze fraud patterns")
```

### 3. Traditional Client API

```python
import louieai
import graphistry

# Authenticate with Graphistry
graphistry.register(api=3, username="your_user", password="your_pass")

# Create client and ask questions
client = louieai.LouieClient()
response = client.add_cell("", "Show me patterns in my data")

# Or use the callable interface (v0.2.0+)
response = client("Show me patterns in my data")
```

## Main Components

### [Notebook API](notebook.md)

Streamlined interface optimized for Jupyter notebooks with implicit thread management and easy data access.

### [louie() Factory Function](notebook.md#factory-function)

Flexible factory function for creating callable Louie interfaces with various authentication methods.

### [LouieClient](client.md)

The traditional client class for interacting with Louie.ai. Provides full control over threads, authentication, and responses. Now also callable!

### [Available Agents](../reference/agents.md)

LouieAI provides 40+ specialized agents with semantic understanding:
- **General AI**: LouieAgent (default), TextAgent, CodeAgent
- **Databases with Semantic Layer**: 
  - PostgresAgent, MySQLAgent, DatabricksAgent, SnowflakeAgent, and more
  - Agents learn your schema and build semantic models for intelligent query generation
  - Natural language queries leverage understanding of your business context
- **Visualizations**: GraphAgent, KeplerAgent, PerspectiveAgent, MermaidAgent
- **Direct Execution**: PassthroughAgent variants for each database

```python
# Default agent
lui("Analyze my data")

# Specify a specialized agent
lui("Show user activity", agent="PostgresAgent")
lui("Create network graph", agent="GraphAgent")
```

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

- Python 3.10 or higher
- Active Graphistry account with API access
- Network access to Louie.ai service

## Authentication

Both APIs support multiple authentication methods:

1. **Environment Variables** (recommended for notebooks):
   ```bash
   export GRAPHISTRY_USERNAME=your_username
   export GRAPHISTRY_PASSWORD=your_password
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