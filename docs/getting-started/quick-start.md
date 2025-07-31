# Quick Start Guide

Get up and running with LouieAI in minutes.

## Basic Setup

First, make sure you have LouieAI installed and a Graphistry account set up.

### 1. Install LouieAI

See the [Installation Guide](installation.md) if you haven't installed LouieAI yet.

### 2. Authenticate

See the [Authentication Guide](authentication.md) for detailed authentication options. For a quick start:

```python
import graphistry
from louieai import LouieClient

# Authenticate with PyGraphistry
graphistry.register(api=3, username="your_user", password="your_pass")

# LouieAI automatically uses the PyGraphistry authentication
client = LouieClient()
```

### 3. Your First Query

#### Thread-based Conversation

```python
# Create a thread with an initial query
thread = client.create_thread(
    name="Data Analysis",
    initial_prompt="What insights can you find about sales trends?"
)

# Continue the conversation in the same thread
response = client.add_cell(
    thread.id,
    "Can you create a visualization of the top 10 products?"
)

# Access response data
if response.type == "TextElement":
    print(response.text)
elif response.type == "DfElement":
    df = response.to_dataframe()
```

Louie maintains conversation context within threads, allowing for sophisticated multi-step analyses.

#### Simple One-Shot Query

For quick queries without thread context:

```python
# Simple ask() method for backward compatibility
response = client.ask("What are the key metrics in the dataset?")
print(response.text)
```

## Error Handling

The LouieClient provides comprehensive error handling:

```python
try:
    thread = client.create_thread(
        initial_prompt="Analyze customer churn patterns"
    )
    response = client.add_cell(thread.id, "Show me the top risk factors")
except RuntimeError as e:
    print(f"Error occurred: {e}")
```

The client distinguishes between different error types:
- **HTTP Errors (4xx/5xx)**: Extracts error messages from API responses
- **Network Errors**: Provides connection failure details
- **Authentication Errors**: Clear guidance when Graphistry token is missing

## Next Steps

- **[Examples Guide](../guides/examples.md)** - Practical examples and use cases
- **[Query Patterns](../guides/query-patterns.md)** - Advanced query techniques
- **[Authentication Guide](authentication.md)** - Multi-tenant usage, API keys, and more
- **[API Reference](../api/index.md)** - Complete API documentation