# LouieAI Python Client

Welcome to the **LouieAI** Python client library documentation.

**LouieAI** is Graphistry's genAI-native investigation platform. This library allows Python applications to interact with LouieAI via its API, leveraging Graphistry authentication.

## Installation

Requires Python 3.11+ and an existing Graphistry account.

Using uv (recommended):
```bash
uv pip install louieai
```

Using pip:
```bash
pip install louieai
```

For development or latest features:
```bash
# With uv
uv pip install git+https://github.com/<owner>/louieai.git

# With pip  
pip install git+https://github.com/<owner>/louieai.git
```

## Usage Example

```python
import graphistry
from louieai import LouieClient

# First, authenticate with Graphistry (replace with your credentials or key)
graphistry.register(api=3, username="your_user", password="your_pass")

client = LouieClient()
response = client.ask("What insights can you find about X dataset?")
print(response)
```

This will send the prompt to LouieAI and return a response (e.g., an answer or a visualization link).

## Error Handling

The LouieClient provides comprehensive error handling with detailed messages:

```python
try:
    client = LouieClient()
    response = client.ask("Your query here")
    print(response)
except RuntimeError as e:
    print(f"Error occurred: {e}")
```

The client distinguishes between different error types:
- **HTTP Errors (4xx/5xx)**: Extracts error messages from API responses
- **Network Errors**: Provides connection failure details
- **Authentication Errors**: Clear guidance when Graphistry token is missing

## Current Status

This library is in active development (Alpha). The `/api/ask` endpoint is based on common REST patterns and is subject to confirmation when official API documentation becomes available.

See the [Architecture](architecture.md) page for more details on how LouieAI and Graphistry integrate.