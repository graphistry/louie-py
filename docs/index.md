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

## Authentication

LouieAI supports multiple authentication methods:

```python
from louieai import LouieClient

# Method 1: Use existing graphistry authentication
import graphistry
graphistry.register(api=3, username="your_user", password="your_pass")
client = LouieClient()

# Method 2: Pass credentials directly
client = LouieClient(
    username="your_user",
    password="your_pass",
    server="hub.graphistry.com"
)

# Method 3: Use register method
client = LouieClient()
client.register(username="your_user", password="your_pass")

# Method 4: Use existing graphistry client
g = graphistry.nodes(df).edges(df2)
client = LouieClient(graphistry_client=g)
```

## Usage Example

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

## Simple One-Shot Queries

For quick queries without thread context:

```python
# Simple ask() method for backward compatibility
response = client.ask("What are the key metrics in the dataset?")
print(response.text)
```

## Error Handling

The LouieClient provides comprehensive error handling with detailed messages:

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

## Key Features

- **Thread-based conversations**: Maintain context across multiple queries
- **Multiple response types**: Handle text, DataFrames, visualizations, and more
- **Streaming support**: Responses stream in real-time via JSONL
- **Natural language interface**: Access all Louie capabilities through simple prompts
- **Auto-refresh authentication**: Automatically handles JWT token expiration
- **Multiple auth methods**: Works with existing Graphistry sessions or direct credentials

See the [Architecture](architecture.md) page for more details on how LouieAI and Graphistry integrate.