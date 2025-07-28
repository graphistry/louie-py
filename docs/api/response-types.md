# Response Types Reference

Louie.ai returns different types of elements based on your natural language queries. Understanding these types helps you handle responses effectively.

## Overview

The beauty of Louie's API is that you don't need different methods for different capabilities - just ask in natural language and Louie returns the appropriate response type.

```python
# Simple query, appropriate response
response = client.add_cell(thread.id, "Your request in natural language")
```

## Common Response Types

### DataFrame Responses (DfElement)

When you query databases or request tabular data, Louie returns a DataFrame element.

**Common Queries:**
- "Query PostgreSQL for user statistics"
- "Get sales data from ClickHouse"
- "Search Splunk logs for errors"

**Handling:**
```python
response = client.add_cell(thread.id, "Query sales database for Q4 revenue")

# Check if response has a DataFrame
if response.to_dataframe() is not None:
    df = response.to_dataframe()
    print(f"Retrieved {len(df)} rows")
    print(df.head())
```

### Text/Insights Responses (TextElement)

When you ask for explanations, summaries, or insights, Louie returns text elements.

**Common Queries:**
- "Summarize the key findings"
- "Explain the correlation between X and Y"
- "Generate an executive summary"

**Handling:**
```python
response = client.add_cell(thread.id, "Analyze trends and provide insights")

# Access text content
if response.content:
    print(response.content)  # Markdown-formatted insights
```

### Visualization Responses

Louie can generate various types of visualizations, each with its own response type.

#### Graphistry Network Graphs (GraphElement)

**Common Queries:**
- "Visualize user connections in Graphistry"
- "Create a network graph of system dependencies"
- "Show fraud patterns as a graph"

**Handling:**
```python
response = client.add_cell(thread.id, 
    "Visualize customer relationships in Graphistry for users who bought product X"
)

if hasattr(response, 'dataset_id'):
    # Build Graphistry URL
    viz_url = f"https://hub.graphistry.com/graph/graph.html?dataset={response.dataset_id}"
    print(f"View visualization: {viz_url}")
```

#### Geographic Maps (KeplerElement)

**Common Queries:**
- "Create a Kepler map of customer locations"
- "Show delivery routes on a map"
- "Visualize regional sales as a heatmap"

**Handling:**
```python
response = client.add_cell(thread.id,
    "Create a Kepler map showing customer density by region"
)

if response.type == "KeplerElement":
    # Access map configuration
    print(f"Map created: {response.title}")
    # Map config available in response.config
```

#### Charts and Heatmaps (PerspectiveElement)

**Common Queries:**
- "Create a heatmap of sales by region and month"
- "Generate a pivot table of expenses by department"
- "Build an interactive chart of trends"

**Handling:**
```python
response = client.add_cell(thread.id,
    "Create a Perspective heatmap of activity by hour and day of week"
)

if response.type == "PerspectiveElement":
    # Chart configuration available
    print("Interactive chart created")
```

### Error Responses (ExceptionElement)

When queries encounter errors, Louie returns detailed error information.

**Handling:**
```python
response = client.add_cell(thread.id, "Query non_existent_table")

if response.type == "ExceptionElement":
    print(f"Error: {response.text}")
    if response.traceback:
        print(f"Traceback: {response.traceback}")
```

## Multi-Element Responses

Complex queries can return multiple elements in a single response.

```python
response = client.add_cell(thread.id, """
    1. Query PostgreSQL for customer data
    2. Create a UMAP clustering visualization
    3. Use TableAI to identify anomalies
    4. Summarize the findings
""")

# Handle multiple elements
elements = response.elements  # List of different element types

for element in elements:
    if element.type == "DfElement":
        df = element.to_dataframe()
        print(f"Data: {len(df)} rows")
    
    elif element.type == "GraphElement":
        print(f"Visualization: {element.dataset_id}")
    
    elif element.type == "TextElement":
        print(f"Insights: {element.text}")
```

## Type Detection Patterns

### Method 1: Duck Typing
```python
def handle_response(response):
    # Check for DataFrame
    if hasattr(response, 'to_dataframe') and response.to_dataframe() is not None:
        return handle_dataframe(response.to_dataframe())
    
    # Check for visualization
    if hasattr(response, 'dataset_id'):
        return handle_visualization(response)
    
    # Check for text
    if hasattr(response, 'content'):
        return handle_text(response.content)
```

### Method 2: Type Property
```python
def handle_response_by_type(response):
    response_handlers = {
        'DfElement': handle_dataframe,
        'GraphElement': handle_graph,
        'TextElement': handle_text,
        'ExceptionElement': handle_error,
        'KeplerElement': handle_map,
        'PerspectiveElement': handle_chart
    }
    
    handler = response_handlers.get(response.type, handle_unknown)
    return handler(response)
```

### Method 3: Try-Except Pattern
```python
def safe_handle_response(response):
    try:
        # Try DataFrame first (most common)
        df = response.to_dataframe()
        if df is not None:
            return process_dataframe(df)
    except AttributeError:
        pass
    
    try:
        # Try text content
        if response.content:
            return process_text(response.content)
    except AttributeError:
        pass
    
    # Handle other types...
```

## Advanced Response Handling

### Streaming Responses
For long-running queries, responses may be streamed:

```python
response = client.add_cell(thread.id, "Analyze 10M records...")

# Check status
while response.status == "running":
    print(f"Progress: {response.progress}%")
    time.sleep(1)
    response = client.get_cell_status(thread.id, response.cell_id)
```

### Caching Responses
For expensive queries, cache responses:

```python
import pickle

def cached_query(client, thread_id, query, cache_file):
    try:
        # Try to load from cache
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        # Run query and cache result
        response = client.add_cell(thread_id, query)
        with open(cache_file, 'wb') as f:
            pickle.dump(response, f)
        return response
```

### Custom Response Wrappers
Create your own response wrapper for easier handling:

```python
class LouieResponse:
    def __init__(self, raw_response):
        self.raw = raw_response
        self._dataframe = None
        self._visualizations = []
        self._insights = []
        self._parse_response()
    
    def _parse_response(self):
        # Parse different element types
        if hasattr(self.raw, 'elements'):
            for element in self.raw.elements:
                if element.type == 'DfElement':
                    self._dataframe = element.to_dataframe()
                elif element.type in ['GraphElement', 'KeplerElement']:
                    self._visualizations.append(element)
                elif element.type == 'TextElement':
                    self._insights.append(element.text)
    
    @property
    def dataframe(self):
        return self._dataframe
    
    @property
    def visualizations(self):
        return self._visualizations
    
    @property
    def insights(self):
        return '\n\n'.join(self._insights)
```

## Response Type Quick Reference

| Query Type | Response Type | Key Properties | Common Use Cases |
|------------|---------------|----------------|------------------|
| Database queries | DfElement | `.to_dataframe()` | Data analysis, reporting |
| Visualizations | GraphElement | `.dataset_id` | Network analysis, relationships |
| Maps | KeplerElement | `.config`, `.title` | Geographic analysis |
| Charts | PerspectiveElement | `.config` | Business intelligence |
| Insights | TextElement | `.content`, `.text` | Summaries, explanations |
| Errors | ExceptionElement | `.text`, `.traceback` | Error handling |
| Generated images | Base64ImageElement | `.src` | Matplotlib/Seaborn charts |

## Best Practices

1. **Always handle errors gracefully** - Check for ExceptionElement
2. **Use type detection** - Don't assume response type
3. **Handle multi-element responses** - Complex queries return multiple types
4. **Cache expensive queries** - Especially for large visualizations
5. **Provide feedback** - Show progress for long-running queries

## Next Steps

- See [Query Patterns](../query-patterns.md) for examples of queries that generate each response type