# Examples

This page demonstrates common usage patterns for both the notebook-friendly API and the traditional LouieAI Python client.

## Basic Query

### Notebook API (Recommended for Jupyter)

```python
# Option 1: Traditional import
from louieai.notebook import lui

# Option 2: New callable module (cleaner!)
import louieai
lui = louieai()  # Uses environment variables or existing PyGraphistry auth

# Make a query - returns cursor for chaining
result = lui("What are the top security threats in my data?")

# In Jupyter, the response is displayed automatically
# You can also access it programmatically:
print(lui.text)

# Or chain operations:
summary = lui("Summarize the threats").text
```

### Traditional Client API

```python
import graphistry
import louieai as lui

# Authenticate
graphistry.register(api=3, username="your_user", password="<password>")

# Create client and make a query
client = lui.LouieClient()
response = client.add_cell("", "What are the top security threats in my data?")

# Print the response
for text in response.text_elements:
    print(text['content'])
```

## Advanced API Patterns

### Thread Creation with Initial Query

```python
# Traditional client: Create thread with initial prompt
thread = client.create_thread(
    name="Security Analysis", 
    initial_prompt="Query logs for failed login attempts in last 24 hours"
)
response = thread  # Initial response is returned when thread is created
```

### Handling Different Response Types

```python
# Traditional client: Check response type for images
response = client.add_cell(thread.id, "Create a trend visualization")

if response.type == "Base64ImageElement":
    save_base64_image(response.src, "trends.png")
    
if response.dataset_id:
    print(f"View graph: https://hub.graphistry.com/graph/graph.html?dataset={response.dataset_id}")
```

### Chaining Responses with Data

```python
# Traditional client: Extract data from one response to use in next query
response1 = client.add_cell(thread.id, "Find suspicious IP addresses")
suspicious_ips = response1.to_dataframe()['source_ip'].unique()

response2 = client.add_cell(thread.id, 
    f"Analyze these IPs for threats: {suspicious_ips.tolist()}")
```

## Working with DataFrames

### Getting DataFrames from Queries

```python
# Query that returns data - response displays automatically in Jupyter
lui("Show me a summary of failed login attempts by country")

# Access DataFrame directly
if lui.df is not None:
    print(f"Shape: {lui.df.shape}")
    print(lui.df.head())
    
# Access all dataframes from the response
for i, df in enumerate(lui.dfs):
    print(f"DataFrame {i}: {df.shape}")

# Chain operations on the returned cursor
top_countries = lui("Show top 5 countries by failed logins").df
if top_countries is not None:
    top_countries.plot(kind='bar')
```

### Uploading and Analyzing Your DataFrames

```python
import pandas as pd
import numpy as np

# Create or load your data
df = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=100, freq='D'),
    'sales': np.random.randn(100).cumsum() + 100,
    'category': np.random.choice(['A', 'B', 'C'], 100)
})

# Upload and analyze with natural language
lui("Identify trends and seasonal patterns", df)
print(lui.text)  # AI's analysis

# Get statistical summary
lui(df, "calculate key statistics by category")
stats_df = lui.df  # Access returned statistics

# Find anomalies
lui("Find outliers and unusual patterns", df)

# Complex analysis
lui("""
    Analyze this sales data:
    1. Identify top performing categories
    2. Find any anomalies or outliers
    3. Predict next 30 days trend
""", df)

# Access multiple results
for i, result_df in enumerate(lui.dfs):
    print(f"Result {i+1}: {result_df.shape}")
```

### DataFrame Upload Patterns

```python
# Pattern 1: Prompt first (clear intent)
lui("Calculate correlation matrix", df)

# Pattern 2: DataFrame first (natural for simple ops)
lui(df, "summarize")

# Pattern 3: Ultra-concise
lui("sum", df)

# Pattern 4: With options
lui("Analyze this CSV data", df, 
    format="csv",  # Specify serialization format
    share_mode="Organization")  # Share with team

# Pattern 5: Multi-step analysis
# First upload
lui("Load and profile this dataset", df)

# Follow-up questions on same data
lui("Which features are most correlated?")
lui("Are there any data quality issues?")
lui("Suggest data transformations")
```

### Traditional Client API

```python
# Query that returns data
response = client.add_cell("", "Show me a summary of failed login attempts by country")

# Access DataFrame results
for df_elem in response.dataframe_elements:
    df = df_elem['table']  # This is a pandas DataFrame
    print(f"Shape: {df.shape}")
    print(df.head())
```

## Conversational Analysis

### Notebook API - Automatic Thread Management

```python
# First query automatically creates a thread
lui("Load the security logs from last week")

# Continue the conversation - thread is maintained automatically
lui("Show me the most frequent error codes")

# Ask follow-up questions
lui("Which IP addresses triggered these errors?")

# Access any previous response
first_response_text = lui[-3].text
error_codes_df = lui[-2].df
```

### Creating Separate Analysis Threads

Sometimes you need to analyze different topics without mixing contexts:

```python
# Main security analysis thread
security_lui = louie(name="Security Analysis - Week 47")
security_lui("Load security logs and identify suspicious patterns")
security_lui("Focus on failed authentication attempts")

# Create a separate thread for performance analysis
perf_lui = security_lui.new(name="Performance Analysis - Week 47")
perf_lui("Analyze API response times for the same period")
perf_lui("Which endpoints are slowest?")

# Create a private thread for sensitive investigation
private_lui = security_lui.new(
    name="Executive Dashboard Investigation",
    share_mode="Private"
)
private_lui("Check access patterns to executive dashboards")

# Each thread maintains its own context
security_lui("Back to security - correlate the failed logins with geo data")
perf_lui("Show me the correlation between slow responses and error rates")

# All threads share the same authentication
print(f"Security findings: {security_lui.text}")
print(f"Performance issues: {perf_lui.df}")
print(f"Private investigation: {private_lui.text}")
```

### Traditional Client API - Manual Thread Management

```python
# First query creates a new thread
response1 = client.add_cell("", "Load the security logs from last week")
thread_id = response1.thread_id

# Continue the conversation in the same thread
response2 = client.add_cell(thread_id, "Show me the most frequent error codes")

# Ask follow-up questions
response3 = client.add_cell(thread_id, "Which IP addresses triggered these errors?")
```

## Creating Visualizations

LouieAI can create graph visualizations using Graphistry:

```python
# Request a network visualization
response = client.add_cell(
    "", 
    "Create a network graph showing connections between IP addresses"
)

# Check for graph elements
if response.has_graphs:
    for graph in response.graph_elements:
        print(f"Graph ID: {graph['id']}")
        # The graph is automatically visualized in Graphistry
```

## Error Handling

### Notebook API - Graceful Defaults

```python
# The notebook API returns None/empty instead of raising exceptions
lui("Analyze the data")

# Check for errors in the response
if lui.has_errors:
    print("Query completed with errors:")
    for error in lui.errors:
        print(f"Error: {error.get('message', 'Unknown error')}")
else:
    # Safe access - no exceptions
    if lui.text:
        print(lui.text)
    if lui.df is not None:
        print(f"Data shape: {lui.df.shape}")
```

### Traditional Client API

```python
try:
    response = client.add_cell("", "Analyze the data")
    
    # Process response
    for text in response.text_elements:
        print(text['content'])
            
except Exception as e:
    print(f"Request failed: {e}")
```

## Using with Existing Graphistry Workflows

Integrate LouieAI with your existing Graphistry visualizations:

```python
import pandas as pd
import graphistry

# Your existing data
df = pd.DataFrame({
    'source': ['A', 'B', 'C'],
    'target': ['B', 'C', 'A'],
    'weight': [1, 2, 3]
})

# Create a Graphistry object
g = graphistry.edges(df, 'source', 'target')

# Pass it to LouieAI
client = lui.LouieClient(graphistry_client=g)
response = client.add_cell("", "What patterns do you see in this network?")
```

For advanced authentication options including multi-tenant usage, API keys, and concurrent sessions, see the [Authentication Guide](authentication.md).

## Advanced Features

### Enable AI Reasoning Traces

```python
# Notebook API
lui.traces = True  # Enable for all queries
lui("Complex analysis requiring step-by-step reasoning")

# Or enable for single query
lui("Another complex query", traces=True)

# Traditional API
response = client.add_cell("", "Complex analysis", traces=True)
```

### Access Full Response History

```python
# Notebook API - built-in history
for i in range(-5, 0):  # Last 5 queries
    try:
        print(f"\nQuery {i}:")
        print(f"Text: {lui[i].text[:100]}...")
        print(f"Has data: {lui[i].df is not None}")
    except IndexError:
        break

# Traditional API requires manual tracking
```

### Batch Analysis

```python
# Notebook API
queries = [
    "Summarize security incidents by severity",
    "Show top 10 affected systems",
    "Calculate average response time"
]

results = []
for query in queries:
    lui(query)
    results.append({
        'query': query,
        'has_data': lui.df is not None,
        'summary': lui.text[:100] if lui.text else None
    })
```

## Notebook-Specific Features

### Auto-Display in Jupyter

```python
import louieai
lui = louieai()

# In Jupyter, responses display automatically with formatting
lui("Explain the key findings")
# ✨ Response appears below the cell with markdown rendering

# Disable auto-display for a specific query
lui("Generate large report", display=False)
```

### Method Chaining

```python
# Chain operations on the cursor
analysis = lui("Analyze user behavior patterns") \
    .df \
    .groupby('user_type') \
    .agg({'activity_count': 'sum'})

# Multiple queries in sequence
lui("Load user data") \
   ("Filter for active users") \
   ("Show summary statistics")
```

### Clean Import Patterns

```python
# Method 1: Direct module call (NEW!)
import louieai
lui = louieai(username="user", password="<password>")

# Method 2: Traditional notebook import
from louieai.notebook import lui

# Method 3: With PyGraphistry client
import graphistry
g = graphistry.register(api=3, server="hub.graphistry.com", username="user", password="<password>")
lui = louieai(g, server_url="https://den.louie.ai")
```

## Interactive Notebooks

For hands-on examples, check out our example notebooks:

- **[Getting Started](../getting-started/notebooks/01-getting-started.ipynb)** - Basic usage tutorial
- **[Data Science Workflow](../getting-started/notebooks/02-data-science-workflow.ipynb)** - Complete analysis workflow
- **[Fraud Investigation](../getting-started/notebooks/03-fraud-investigation.ipynb)** - Real-world use case
- **[Error Handling](../getting-started/notebooks/04-error-handling.ipynb)** - Robust error handling patterns

## Next Steps

- Check out the [API Reference](../api/index.md) for detailed documentation
- Learn about [Query Patterns](query-patterns.md) for advanced usage
- Explore the [Architecture](../developer/architecture.md) to understand how LouieAI works
- Try the [Notebook API Reference](../api/notebook.md) for the complete notebook interface