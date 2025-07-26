# API Reference

This section contains the complete API reference for the LouieAI Python client library.

## Overview

The LouieAI client provides a simple interface for interacting with the Louie.ai service:

```python
import louieai
import graphistry

# Authenticate with Graphistry
graphistry.register(api=3, username="your_user", password="your_pass")

# Create client and ask questions
client = louieai.LouieClient()
response = client.ask("Show me patterns in my data")
```

## Main Components

### [LouieClient](client.md)

The primary class for interacting with Louie.ai. Handles authentication, requests, and error management.

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

- Python 3.11 or higher
- Active Graphistry account with API access
- Network access to Louie.ai service

## Error Handling

All API methods raise `RuntimeError` exceptions on failure. See the [LouieClient documentation](client.md) for detailed error handling examples.