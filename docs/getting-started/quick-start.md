# Quick Start Guide

Get up and running with LouieAI in minutes. This guide covers both the notebook-friendly API and the traditional client API.

## Basic Setup

First, make sure you have LouieAI installed and a Graphistry account set up.

### 1. Install LouieAI

See the [Installation Guide](installation.md) if you haven't installed LouieAI yet.

### 2. Choose Your API Style

LouieAI offers two API styles:

#### Notebook-Friendly API (Recommended for Jupyter)

```python
from louieai.notebook import lui

# That's it! Authentication uses environment variables:
# export LOUIE_USER=your_username
# export LOUIE_PASS=your_password
```

#### Traditional Client API

```python
import graphistry
from louieai import LouieClient

# Authenticate with PyGraphistry Hub
graphistry.register(api=3, server="hub.graphistry.com", username="your_user", password="your_pass")

# Connect to Louie Den (default detective AI service)
client = LouieClient(server_url="https://den.louie.ai")
```

See the [Authentication Guide](authentication.md) for detailed authentication options.

### 3. Your First Query

#### Notebook-Friendly API

```python
# Ask questions naturally
lui("What insights can you find about sales trends?")

# Access the response immediately
print(lui.text)  # Text response
df = lui.df      # DataFrame (if any)

# Continue the conversation
lui("Can you create a visualization of the top 10 products?")

# Access history
previous_df = lui[-1].df  # Previous response's dataframe
```

#### Traditional Client API

```python
# Create a thread and ask questions
response = client.add_cell("", "What insights can you find about sales trends?")

# Access response data
if response.text_elements:
    print(response.text_elements[0]['content'])
if response.dataframe_elements:
    df = response.dataframe_elements[0]['table']
```

Both APIs maintain conversation context, allowing for sophisticated multi-step analyses.

## Working with Data

### Notebook API

```python
# Generate some data
lui("Create a sample sales dataset with 100 rows")

# Access the data
if lui.df is not None:
    print(f"Generated {len(lui.df)} rows")
    print(lui.df.head())
    
    # Work with the data
    sales_by_region = lui.df.groupby('region')['sales'].sum()
```

### Traditional API

```python
# Generate data
response = client.add_cell("", "Create a sample sales dataset with 100 rows")

# Access the data
if response.dataframe_elements:
    df = response.dataframe_elements[0]['table']
    print(f"Generated {len(df)} rows")
```

## Error Handling

### Notebook API

The notebook API returns None/empty instead of raising exceptions:

```python
# Safe data access - no exceptions
df = lui.df  # None if no dataframe
texts = lui.texts  # Empty list if no text

# Check for errors in response
if lui.has_errors:
    for error in lui.errors:
        print(f"Error: {error['message']}")
```

### Traditional API

```python
try:
    response = client.add_cell("", "Analyze customer churn patterns")
except RuntimeError as e:
    print(f"Error occurred: {e}")
```

## Advanced Features

### Enable AI Reasoning Traces

```python
# Notebook API
lui.traces = True
lui("Complex analysis query")

# Traditional API  
response = client.add_cell("", "Complex analysis query", traces=True)
```

### Access Response History

```python
# Notebook API
for i in range(-3, 0):
    print(f"Query {i}: {lui[i].text[:50]}...")

# Traditional API requires manual history tracking
```

## Next Steps

- **[Notebook Examples](../notebooks/)** - Interactive Jupyter notebooks
- **[Examples Guide](../guides/examples.md)** - Practical examples and use cases
- **[Query Patterns](../guides/query-patterns.md)** - Advanced query techniques
- **[Authentication Guide](authentication.md)** - Multi-tenant usage, API keys, and more
- **[API Reference](../api/index.md)** - Complete API documentation