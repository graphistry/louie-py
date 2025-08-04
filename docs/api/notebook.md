# Notebook API Reference

The notebook API provides a streamlined interface optimized for Jupyter notebooks and interactive data analysis.

## Quick Start

```python
from louieai.notebook import lui

# Make queries - returns the cursor for chaining
response = lui("Analyze the sales data from last quarter")

# The response is displayed automatically in Jupyter notebooks
# You can also access results directly:
print(lui.text)      # Text response
df = lui.df          # Latest dataframe
all_dfs = lui.dfs    # All dataframes

# Or chain operations:
lui("Show me the data").df.head()
```

## Alternative Import Methods

### Direct Module Import (New!)

The cleanest import method - make the module itself callable:

```python
import louieai

# Create authenticated instance
lui = louieai(username="user", password="<password>")
# Or with existing PyGraphistry client
lui = louieai(g)

# Use it
lui("Your query here")
```

### Global Singleton Import

You can also import the global `lui` singleton from the globals module:

```python
from louieai.globals import lui

# Works the same as importing from notebook
lui("Your query here")
```

## The `lui` Object

The `lui` object is a singleton that manages your LouieAI session with implicit thread management.

### Making Queries

```python
# Basic query - returns the cursor itself for chaining
result = lui("What are the key metrics in this dataset?")
# result is lui, so you can chain: lui("query").df

# Query with traces enabled for this call only
lui("Complex analysis task", traces=True)

# Query without auto-display in Jupyter
lui("Generate report", display=False)
```

**Important**: `lui()` returns itself (the cursor), not the Response object. This enables:
- Chaining operations: `lui("query").df.describe()`
- Immediate property access: `text = lui("query").text`
- Auto-display in Jupyter notebooks

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

The notebook API supports multiple authentication methods via environment variables:

### Personal Key Authentication (Recommended for Service Accounts)

```bash
export GRAPHISTRY_PERSONAL_KEY_ID=your_key_id
export GRAPHISTRY_PERSONAL_KEY_SECRET=your_key_secret
export GRAPHISTRY_ORG_NAME=your_org  # Optional
```

### API Key Authentication (Legacy)

```bash
export GRAPHISTRY_API_KEY=your_api_key
```

### Username/Password Authentication

```bash
export GRAPHISTRY_USERNAME=your_username
export GRAPHISTRY_PASSWORD=your_password
```

### Custom Server URL

```bash
export LOUIE_URL=https://custom-louie.ai  # Custom Louie server
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

### Thread Properties

| Property | Type | Description |
|----------|------|-------------|
| `lui.thread_id` | `str \| None` | Current conversation thread ID |
| `lui.url` | `str \| None` | URL to view current thread in Louie web interface |

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

### Thread Management

Access thread information and share conversation links:

```python
# Get the current thread ID
thread_id = lui.thread_id
print(f"Current thread: {thread_id}")

# Get a shareable URL to view the thread
thread_url = lui.url
print(f"View this conversation at: {thread_url}")

# Example: Share analysis results with your team
lui("Analyze customer churn patterns for Q4")
if lui.url:
    print(f"Share this analysis: {lui.url}")
    # Outputs: Share this analysis: https://den.louie.ai/?dthread=abc123...
```

**Note**: The `.url` property returns `None` if no thread is active yet (before making any queries).

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

### Real-time Streaming Display

When running in Jupyter notebooks, the notebook API automatically streams responses as they're generated, providing a better user experience for long-running queries:

```python
# This query will show progressive updates in Jupyter
lui("Write a detailed analysis of customer behavior patterns")

# You'll see the response building up in real-time
# instead of waiting for the complete response
```

**Features of streaming display:**
- ⚡ **Faster time-to-first-content** - See initial response immediately
- 📊 **Progressive updates** - Watch as the AI builds its response
- 🔄 **Automatic refresh** - Display updates smoothly without flicker
- 📈 **Works with all response types** - Text, dataframes, and errors

**Note**: Streaming display is only active in Jupyter environments. In regular Python scripts, the full response is returned after completion.

## Advanced Usage

### Using the louie() Factory Function

The `louie()` factory function provides a convenient way to create cursors with different authentication methods:

```python
from louieai import louie

# Create cursor with default configuration
cursor = louie()

# Create cursor with PyGraphistry client
import graphistry
g = graphistry.register(api=3, username="user", password="<password>")
cursor = louie(g)

# Create cursor with personal key authentication
cursor = louie(
    personal_key_id="your_key_id",
    personal_key_secret="your_key_secret",
    org_name="your_org"
)

# Create cursor with API key
cursor = louie(api_key="your_api_key")

# Create cursor with thread name and share mode
cursor = louie(name="Security Analysis", share_mode="Organization")

# Use any cursor
cursor("Your query here")
print(cursor.text)
```

### Creating New Conversation Threads

The `new()` method allows you to create fresh conversation threads while preserving all authentication and configuration:

```python
# Start with your main analysis
lui = louie()
lui("Analyze security incidents from last week")

# Create a new thread for a different topic
perf_analysis = lui.new(name="Performance Analysis")
perf_analysis("Show me API response times")

# Create another thread with different visibility
private_investigation = lui.new(
    name="Sensitive Investigation",
    share_mode="Private"
)
private_investigation("Investigate user account anomalies")

# Original thread is unchanged
lui("Continue with security analysis...")  # Still in original thread
```

**Key features of `new()`:**
- **Preserves all configuration**: Authentication, server URLs, timeouts
- **Fresh context**: Each new thread starts without previous conversation history
- **Optional naming**: Provide meaningful names to organize your analyses
- **Share mode control**: Override visibility per thread (Private, Organization, Public)

**Common use cases:**
1. **Organize by topic**: Separate threads for security, performance, business analysis
2. **Isolate investigations**: Keep sensitive queries in private threads
3. **Parallel analysis**: Run different analyses without context confusion
4. **Clean slate**: Start fresh when switching to unrelated topics

### Custom Client Configuration

For more control, you can create a client directly:

```python
from louieai._client import LouieClient
from louieai.notebook import Cursor

# Create custom client with personal key auth
client = LouieClient(
    server_url="https://custom.louie.ai",
    personal_key_id="your_key_id",
    personal_key_secret="your_key_secret",
    org_name="your_org",
    server="hub.graphistry.com"
)

# Or with username/password
client = LouieClient(
    server_url="https://custom.louie.ai",
    username="user",
    password="<password>"
)

# Create cursor with custom client
cursor = Cursor(client=client)

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

## Factory Function

The `louie()` factory function provides flexible ways to create callable Louie interfaces:

```python
from louieai import louie

# 1. Global client (uses environment variables)
lui = louie()

# 2. From existing PyGraphistry client
import graphistry
gc = graphistry.client()
gc.register(api=3, username="user", password="<password>")
lui = louie(gc)

# 3. With direct credentials
lui = louie(username="user", password="<password>")
lui = louie(personal_key_id="pk_123", personal_key_secret="sk_456")
lui = louie(api_key="your_api_key")

# All return a callable interface
response = lui("What insights can you find?")
print(lui.text)
```

### Parameters

- `graphistry_client` (optional): Existing PyGraphistry client instance
- `**kwargs`: Authentication parameters:
  - `username`, `password`: Basic authentication
  - `personal_key_id`, `personal_key_secret`: Service account auth
  - `api_key`: API key authentication
  - `org_name`: Organization name (optional)
  - `server`: PyGraphistry server URL
  - `server_url`: Custom Louie server URL

## Configuration

### Timeout Settings

Long-running agentic workflows may require increased timeouts. You can configure these via environment variables:

```bash
# Overall request timeout (default: 300 seconds / 5 minutes)
export LOUIE_TIMEOUT=600

# Per-chunk streaming timeout (default: 120 seconds / 2 minutes)
export LOUIE_STREAMING_TIMEOUT=180
```

Or configure them when creating a client:

```python
from louieai._client import LouieClient
from louieai.notebook import Cursor

# Create client with custom timeouts
client = LouieClient(
    timeout=600.0,  # 10 minutes overall
    streaming_timeout=180.0  # 3 minutes per chunk
)

# Use with cursor
cursor = Cursor(client=client)
cursor("Long-running analysis task")
```

## See Also

- [Getting Started Notebook](../getting-started/notebooks/01-getting-started.ipynb)
- [Examples Guide](../guides/examples.md)
- [Traditional Client API](client.md)