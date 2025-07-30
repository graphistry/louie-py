# Examples

This page demonstrates common usage patterns for the LouieAI Python client.

## Basic Query

The simplest way to use LouieAI is to send a natural language query:

```python
import graphistry
import louieai as lui

# Authenticate
graphistry.register(api=3, username="your_user", password="your_pass")

# Create client and make a query
client = lui.Client()
response = client.add_cell("", "What are the top security threats in my data?")

# Print the response
for text in response.text_elements:
    print(text['text'])
```

## Working with DataFrames

LouieAI can analyze data and return DataFrames:

```python
# Query that returns data
response = client.add_cell("", "Show me a summary of failed login attempts by country")

# Access DataFrame results
for df_elem in response.dataframe_elements:
    df = df_elem['table']  # This is a pandas DataFrame
    print(f"Shape: {df.shape}")
    print(df.head())
```

## Thread-based Conversations

Maintain context across multiple queries using threads:

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

Handle errors gracefully:

```python
try:
    response = client.add_cell("", "Analyze the data")
    
    # Check for errors in the response
    if response.has_errors:
        print("Query completed with errors:")
        for elem in response.elements:
            if elem.get('type') == 'ExceptionElement':
                print(f"Error: {elem.get('message', 'Unknown error')}")
    else:
        # Process successful response
        for text in response.text_elements:
            print(text['text'])
            
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
client = lui.Client(graphistry_client=g)
response = client.add_cell("", "What patterns do you see in this network?")
```

## Direct Authentication

Pass credentials directly to the client:

```python
# Instead of using graphistry.register()
client = lui.Client(
    username="your_user",
    password="your_pass",
    server="hub.graphistry.com"
)

# Or use API key
client = lui.Client(
    api_key="your_api_key",
    server="hub.graphistry.com"
)
```

## Managing Threads

List and retrieve existing conversation threads:

```python
# List recent threads
threads = client.list_threads(page=1, page_size=10)
for thread in threads:
    print(f"Thread {thread.id}: {thread.name}")

# Get a specific thread
thread = client.get_thread("thread_id_here")

# Continue conversation in existing thread
response = client.add_cell(thread.id, "Continue our previous analysis")
```

## Next Steps

- Check out the [API Reference](api/index.md) for detailed documentation
- Learn about [Query Patterns](query-patterns.md) for advanced usage
- Explore the [Architecture](architecture.md) to understand how LouieAI works