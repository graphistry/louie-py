# Quick Start Guide

Get up and running with LouieAI in minutes using the notebook-friendly API.

## 1. Install LouieAI

See the [Installation Guide](installation.md) if you haven't installed LouieAI yet.

## 2. Set Up Authentication

Set your Graphistry credentials as environment variables:

```bash
export GRAPHISTRY_USERNAME=your_username
export GRAPHISTRY_PASSWORD=your_password
```

For other authentication methods, see the [Authentication Guide](authentication.md).

## 3. Start Using LouieAI

```python
from louieai.notebook import lui

# Ask questions naturally
lui("What insights can you find about sales trends?")

# Access the response immediately
print(lui.text)  # Text response
df = lui.df      # DataFrame (if any)

# Continue the conversation
lui("Can you create a visualization of the top 10 products?")
```

## Working with Data

### Getting Data from LouieAI

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

### Analyzing Your Own DataFrames

Upload and analyze your own pandas DataFrames with natural language:

```python
import pandas as pd

# Load your data
df = pd.read_csv("your_data.csv")

# Upload and analyze with a prompt
lui("What are the main trends in this data?", df)
print(lui.text)  # AI's analysis

# Simple operations with reversed syntax
lui(df, "summarize")  # Quick summary
lui(df, "find outliers")  # Anomaly detection

# Ultra-concise for basic operations
sales_df = pd.DataFrame({"Q1": [100, 200], "Q2": [150, 250]})
lui("sum", sales_df)  # Calculate totals

# Continue analysis in the same thread
lui("Now show me year-over-year growth")
```

## Error Handling

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

## Advanced Features

```python
# Enable AI reasoning traces
lui.traces = True
lui("Complex analysis query")

# Access response history
previous_df = lui[-1].df  # Previous response's dataframe
for i in range(-3, 0):
    print(f"Query {i}: {lui[i].text[:50]}...")
```

## Next Steps

- **[Notebook Examples](notebooks/01-getting-started.ipynb)** - Interactive Jupyter notebooks
- **[Examples Guide](../guides/examples.md)** - Practical examples and use cases
- **[Query Patterns](../guides/query-patterns.md)** - Advanced query techniques
- **[Authentication Guide](authentication.md)** - Multi-tenant usage, API keys, and more
- **[API Reference](../api/index.md)** - Complete API documentation