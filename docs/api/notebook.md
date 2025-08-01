# Notebook API Reference

The notebook API provides a streamlined interface optimized for Jupyter notebooks and interactive data analysis.

## Quick Start

```python
from louieai.notebook import lui

# Make queries
lui("Analyze the sales data from last quarter")

# Access results
print(lui.text)      # Text response
df = lui.df          # Latest dataframe
all_dfs = lui.dfs    # All dataframes
```

## The `lui` Object

The `lui` object is a singleton that manages your LouieAI session with implicit thread management.

### Making Queries

```python
# Basic query
lui("What are the key metrics in this dataset?")

# Query with traces enabled for this call only
lui("Complex analysis task", traces=True)

# Query without auto-display in Jupyter
lui("Generate report", display=False)
```

### Accessing Responses

#### Text Responses

```python
# Get the primary text response
text = lui.text  # Returns str or None

# Get all text elements
texts = lui.texts  # Returns list[str]
```

#### DataFrame Access

```python
# Get the latest dataframe (first one if multiple)
df = lui.df  # Returns pd.DataFrame or None

# Get all dataframes from latest response
dfs = lui.dfs  # Returns list[pd.DataFrame]

# Safe access pattern
if lui.df is not None:
    print(f"Data shape: {lui.df.shape}")
    # Work with the dataframe
```

#### Other Elements

```python
# Get all elements with type information
elements = lui.elements  # Returns list[dict]
# Each element has 'type' and 'value' keys

# Check for errors
if lui.has_errors:
    for error in lui.errors:
        print(f"Error: {error['message']}")
```

### Response History

Access previous responses using negative indexing:

```python
# Access previous responses
lui[-1].text  # Previous response text
lui[-2].df    # DataFrame from 2 queries ago

# Iterate through recent history
for i in range(-5, 0):
    try:
        print(f"Query {i}: {lui[i].text[:50]}...")
    except IndexError:
        break  # No more history
```

### Configuration

#### Trace Control

```python
# Enable traces for all queries
lui.traces = True

# Check current trace setting
if lui.traces:
    print("Traces are enabled")

# Disable traces
lui.traces = False
```

## Environment Variables

The notebook API uses environment variables for authentication:

```bash
export LOUIE_USER=your_username
export LOUIE_PASS=your_password
export LOUIE_SERVER=your_server  # Optional, defaults to hub
export LOUIE_URL=https://custom-louie.ai  # Optional
```

Alternatively, it will use existing Graphistry authentication:

```bash
export GRAPHISTRY_USERNAME=your_username
export GRAPHISTRY_PASSWORD=your_password
```

## Properties Reference

### Data Access Properties

| Property | Type | Description |
|----------|------|-------------|
| `lui.text` | `str \| None` | Primary text from latest response |
| `lui.texts` | `list[str]` | All text elements from latest response |
| `lui.df` | `pd.DataFrame \| None` | First dataframe from latest response |
| `lui.dfs` | `list[pd.DataFrame]` | All dataframes from latest response |
| `lui.elements` | `list[dict]` | All elements with type tags |
| `lui.errors` | `list[dict]` | Error elements from latest response |
| `lui.has_errors` | `bool` | Whether latest response contains errors |

### Configuration Properties

| Property | Type | Description |
|----------|------|-------------|
| `lui.traces` | `bool` | Get/set trace setting for session |

### History Access

| Syntax | Description |
|--------|-------------|
| `lui[-1]` | Previous response |
| `lui[-2]` | Response from 2 queries ago |
| `lui[index]` | Access response by index |

## Error Handling

The notebook API is designed to be exception-free for common operations:

```python
# These never raise exceptions, return None/empty instead
df = lui.df          # None if no dataframe
text = lui.text      # None if no text
dfs = lui.dfs        # Empty list if no dataframes

# Check for API errors
if lui.has_errors:
    # Handle errors without exceptions
    for error in lui.errors:
        print(f"Error type: {error.get('error_type')}")
        print(f"Message: {error.get('message')}")
```

## Jupyter Integration

The `lui` object provides rich display in Jupyter notebooks:

```python
# In a Jupyter cell
lui  # Shows status, history count, trace setting

# Use ? for quick help
lui?  # Shows docstring with examples

# Use help() for detailed documentation
help(lui)
```

## Advanced Usage

### Custom Client Configuration

```python
from louieai import LouieClient
from louieai.notebook import GlobalCursor

# Create custom client
client = LouieClient(
    server_url="https://custom.louie.ai",
    username="user",
    password="pass"
)

# Create cursor with custom client
cursor = GlobalCursor(client=client)

# Use the cursor
cursor("Your query here")
```

### Resetting Session

```python
# To start a fresh session, reimport
from louieai.notebook import lui

# This creates a new cursor with fresh history
```

## Best Practices

1. **Use environment variables** for credentials to keep notebooks shareable
2. **Check for None** when accessing dataframes: `if lui.df is not None:`
3. **Use history** for comparing results: `lui[-1].df` vs `lui.df`
4. **Enable traces** only when needed to avoid performance overhead
5. **Handle errors gracefully** using `lui.has_errors` instead of try/except

## See Also

- [Getting Started Notebook](../notebooks/01-getting-started.ipynb)
- [Examples Guide](../guides/examples.md)
- [Traditional Client API](client.md)