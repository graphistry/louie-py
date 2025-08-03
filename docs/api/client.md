# Client API (Advanced)

> **Note**: For most users, we recommend using the [Notebook API](notebook.md) with the `lui` interface. This page documents the lower-level client API for advanced use cases.

## Overview

The LouieClient is the core class that handles communication with the Louie.ai service. While it's now an internal class (`louieai._client.LouieClient`), you can still access its functionality through the public API.

## Creating a Client

### Using the louie() Factory (Recommended)

```python
from louieai import louie
import graphistry

# First authenticate with Graphistry
graphistry.register(api=3, username="your_user", password="your_pass")

# Create a callable cursor
lui = louie()

# Use it like the notebook API
response = lui("Analyze the network patterns in my dataset")
print(lui.text)
```

### Direct Instantiation (Advanced)

For advanced use cases where you need direct access to the client:

```python
from louieai import louie
import graphistry

# Authenticate and get graphistry client
g = graphistry.register(api=3, username="your_user", password="your_pass")

# Create cursor with specific configuration
lui = louie(g)

# Access the underlying client if needed
client = lui._client  # Note: This is accessing internal API
```

## Thread Management

### Using the Cursor API

```python
from louieai import louie

# Create cursor
lui = louie()

# Threads are managed automatically
lui("Start analyzing the network data")
thread_id = lui._client._current_thread_id  # Access current thread

# Continue in same thread
lui("Focus on the largest connected component")

# Start a new thread
lui("", display=False)  # Empty query creates new thread
lui("New topic here")
```

### Low-Level Thread Operations

If you need direct thread control:

```python
from louieai import louie
lui = louie()

# Access the internal client
client = lui._client

# List threads
threads = client.list_threads()
for thread in threads:
    print(f"{thread.id}: {thread.name}")

# Get specific thread
thread = client.get_thread(thread_id)
```

## Response Handling

Responses are automatically parsed and made available through the cursor interface:

```python
from louieai import louie
lui = louie()

# Make a query
lui("Generate a summary report of the data")

# Access different response types
if lui.text:
    print("Text response:", lui.text)

if lui.df is not None:
    print("DataFrame shape:", lui.df.shape)

# Access raw response elements
for element in lui.elements:
    print(f"Element type: {element['type']}")
```

## Error Handling

```python
from louieai import louie
# Example showing error handling (requires authentication)
# lui = louie()
# 
# try:
#     lui("Query the sales database")
# except RuntimeError as e:
#     if "No Graphistry API token" in str(e):
#         print("Please authenticate with graphistry.register() first")
#     elif "API returned error" in str(e):
#         print(f"Server error: {e}")
#     elif "Failed to connect" in str(e):
#         print(f"Network error: {e}")

# Working example with mock authentication
import os
os.environ['GRAPHISTRY_USERNAME'] = 'test'
os.environ['GRAPHISTRY_PASSWORD'] = 'test'
# In practice, use real credentials or graphistry.register()
```

## Configuration Options

### Custom Server URL

```python
from louieai import louie

# Use a custom Louie server
lui = louie(server_url="https://custom.louie.ai")
```

### Authentication Methods

```python
from louieai import louie

# Username/Password
lui = louie(username="user", password="pass")

# Personal Key (Service Account)
lui = louie(
    personal_key_id="pk_123",
    personal_key_secret="sk_456",
    org_name="my-org"
)

# API Key (Legacy)
lui = louie(api_key="your_api_key")
```

### Trace Control

```python
from louieai import louie
lui = louie()

# Enable traces for debugging
lui.traces = True
lui("Complex analysis query")

# Or per-query
lui("Another query", traces=True)
```

### Timeout Configuration

Agentic flows can take significant time to complete. The client provides configurable timeouts:

```python
from louieai import louie

# Default timeouts (5 minutes total, 2 minutes per streaming chunk)
lui = louie()

# Custom timeouts for long-running analysis
lui = louie(
    timeout=600,  # 10 minutes total
    streaming_timeout=180  # 3 minutes per chunk
)

# Using environment variables
# export LOUIE_TIMEOUT=600
# export LOUIE_STREAMING_TIMEOUT=180
lui = louie()  # Will use env var settings
```

If you see timeout errors, the client will provide helpful guidance about increasing timeouts.

## Migration from Direct LouieClient

If you have code using the old `LouieClient` directly:

```python
# Old way (no longer public)
# from louieai import LouieClient
# client = LouieClient()
# response = client.add_cell("", "Query")

# New way
from louieai import louie
lui = louie()
lui("Query")
response = lui._response  # If you need the raw response
```

## See Also

- [Notebook API Reference](notebook.md) - Recommended high-level API
- [Response Types](response-types.md) - Understanding response formats
- [Authentication Guide](../guides/authentication.md) - Detailed auth setup