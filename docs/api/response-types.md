# Response Types Reference

LouieAI returns different types of elements based on your queries. This guide explains the actual response structure and how to handle different element types.

## Overview

The beauty of LouieAI's API is that you ask in natural language and get appropriate response types. The notebook API (`lui`) provides the easiest way to access responses, while the traditional client API gives you raw access to response elements.

## Response Structure

### Notebook API (Recommended)

The notebook API automatically parses responses for easy access:

```python
from louieai.notebook import lui

# Make a query
lui("Generate sales data and create a visualization")

# Access parsed results
text = lui.text          # Primary text response (str or None)
df = lui.df             # Primary dataframe (pd.DataFrame or None) 
all_dfs = lui.dfs       # All dataframes (list[pd.DataFrame])
elements = lui.elements  # Raw elements (list[dict])

# Check for errors
if lui.has_errors:
    for error in lui.errors:
        print(f"Error: {error.get('message')}")
```

### Traditional Client API

The raw response contains a list of elements with type information:

```python
from louieai import louie
lui = louie()

# Access raw response
lui("Query database for customer data")
response = lui._response  # Raw Response object

# Elements are dictionaries with type and data
for element in response.elements:
    element_type = element.get("type")
    print(f"Element type: {element_type}")
```

## Element Types

### Text Elements

**Type:** `"text"`

Text elements contain natural language responses, insights, and explanations.

```python
# Notebook API
lui("Analyze the trends in this data")
text_content = lui.text  # Automatically extracts text

# Raw element structure
{
    "type": "text", 
    "text": "Based on the analysis, I found three key trends..."
}
```

### DataFrame Elements  

**Type:** `"dataframe"`

DataFrame elements contain tabular data from database queries or generated datasets.

```python
# Notebook API  
lui("Generate customer sales data")
df = lui.df  # Automatically converts to pandas DataFrame

# Raw element structure
{
    "type": "dataframe",
    "table": pandas_dataframe_object,
    "df_id": "B_7BwhTIvv"  # Unique identifier for the dataframe
}
```

### Graphistry Visualizations

**Type:** `"graphistry"`

Network visualizations created with Graphistry.

```python
# Notebook API
lui("Create a network graph of customer relationships")

# Access via elements
for element in lui.elements:
    if element.get("type") == "graphistry":
        dataset_id = element.get("dataset_id")
        url = f"https://hub.graphistry.com/graph/graph.html?dataset={dataset_id}"
        print(f"View graph: {url}")

# Raw element structure
{
    "type": "graphistry",
    "dataset_id": "abc123",
    "thread_id": "thread_456"
}
```

### Kepler Maps

**Type:** `"kepler"`

Interactive geospatial maps using Kepler.gl.

```python
# Notebook API
lui("Create a map of customer locations")

# Access map elements
for element in lui.elements:
    if element.get("type") == "kepler":
        print(f"Map title: {element.get('title', 'Untitled Map')}")

# Raw element structure  
{
    "type": "kepler",
    "title": "Customer Distribution Map",
    "config": {...},  # Kepler.gl configuration
    "data": {...}     # GeoJSON or CSV data
}
```

### Perspective Tables

**Type:** `"perspective"`

Interactive data tables and charts using Perspective.js.

```python
# Notebook API
lui("Create an interactive pivot table of sales by region")

# Access perspective elements
for element in lui.elements:
    if element.get("type") == "perspective":
        print("Interactive table created")

# Raw element structure
{
    "type": "perspective", 
    "config": {...},  # Perspective configuration
    "data": {...}     # Table data
}
```

### Error Elements

**Type:** `"error"`

Error information when queries fail or encounter issues.

```python
# Notebook API
lui("Query nonexistent_table")
if lui.has_errors:
    for error in lui.errors:
        print(f"Error: {error.get('message')}")
        print(f"Type: {error.get('error_type')}")

# Raw element structure
{
    "type": "error",
    "message": "Table 'nonexistent_table' not found",
    "error_type": "DatabaseError",
    "traceback": "..."  # Optional traceback
}
```

### Code Elements

**Type:** `"code"`

Generated Python code from CodeAgent.

```python
# Notebook API
lui("Generate code to analyze this dataset", agent="CodeAgent")

for element in lui.elements:
    if element.get("type") == "code":
        print(f"Generated code:\n{element.get('code')}")

# Raw element structure  
{
    "type": "code",
    "code": "import pandas as pd\ndf = pd.read_csv('data.csv')",
    "language": "python"
}
```

## Working with Multiple Elements

Complex queries often return multiple element types:

```python
lui("""
1. Query the sales database
2. Create a visualization  
3. Analyze the trends
""")

# Notebook API automatically separates types
print(f"Text insights: {lui.text}")
print(f"Data shape: {lui.df.shape if lui.df is not None else 'No data'}")

# Or iterate through all elements
for element in lui.elements:
    element_type = element.get("type")
    
    if element_type == "text":
        print(f"Insight: {element.get('text')}")
    elif element_type == "dataframe":
        df = element.get("table")
        print(f"Data: {len(df)} rows") 
    elif element_type == "graphistry":
        print(f"Visualization: {element.get('dataset_id')}")
    elif element_type == "error":
        print(f"Error: {element.get('message')}")
```

## Response Properties

### Notebook API Properties

| Property | Type | Description |
|----------|------|-------------|
| `lui.text` | `str \| None` | Primary text from latest response |
| `lui.texts` | `list[str]` | All text elements from latest response |  
| `lui.df` | `pd.DataFrame \| None` | Primary dataframe from latest response |
| `lui.dfs` | `list[pd.DataFrame]` | All dataframes from latest response |
| `lui.elements` | `list[dict]` | Raw elements with type information |
| `lui.errors` | `list[dict]` | Error elements from latest response |
| `lui.has_errors` | `bool` | Whether latest response contains errors |

### Element Properties

Common properties across element types:

| Property | Description | Available in |
|----------|-------------|--------------|
| `type` | Element type identifier | All elements |
| `text` | Text content | Text elements |
| `table` | Pandas DataFrame | DataFrame elements |  
| `df_id` | Unique dataframe identifier | DataFrame elements |
| `dataset_id` | Graphistry dataset ID | Graphistry elements |
| `message` | Error message | Error elements |
| `error_type` | Error classification | Error elements |
| `config` | Visualization configuration | Kepler, Perspective elements |

## Error Handling

The notebook API is designed to be exception-free:

```python
# These never raise exceptions
text = lui.text      # Returns None if no text
df = lui.df         # Returns None if no dataframe  
dfs = lui.dfs       # Returns empty list if no dataframes

# Check for errors without exceptions
if lui.has_errors:
    for error in lui.errors:
        error_msg = error.get("message", "Unknown error")
        error_type = error.get("error_type", "UnknownError")
        print(f"{error_type}: {error_msg}")
```

## Advanced Patterns

### Safe Element Access

```python
def safe_get_dataframe(elements):
    """Safely extract first dataframe from elements."""
    for element in elements:
        if element.get("type") == "dataframe":
            return element.get("table")
    return None

def safe_get_text(elements):
    """Safely extract first text from elements.""" 
    for element in elements:
        if element.get("type") == "text":
            return element.get("text")
    return None

# Usage
df = safe_get_dataframe(lui.elements)
text = safe_get_text(lui.elements)
```

### Type-Based Response Handler

```python
def handle_response_elements(elements):
    """Process all elements by type."""
    results = {
        "dataframes": [],
        "texts": [],
        "visualizations": [],
        "errors": []
    }
    
    for element in elements:
        element_type = element.get("type")
        
        if element_type == "dataframe":
            results["dataframes"].append(element.get("table"))
        elif element_type == "text":
            results["texts"].append(element.get("text"))
        elif element_type in ["graphistry", "kepler", "perspective"]:
            results["visualizations"].append(element)
        elif element_type == "error":
            results["errors"].append(element)
    
    return results

# Usage
lui("Complex multi-step analysis")
results = handle_response_elements(lui.elements)
```

### DataFrame Management

```python
# Save and load dataframes using df_id
lui("Generate customer data")
df_id = None

for element in lui.elements:
    if element.get("type") == "dataframe" and "df_id" in element:
        df_id = element["df_id"]
        break

if df_id:
    # Load the dataframe later
    lui(f"get_dataframe('{df_id}')", agent="CodeAgent")
```

## Best Practices

1. **Use the notebook API** (`lui`) for easier response handling
2. **Always check for None** when accessing `lui.df` or `lui.text`  
3. **Handle errors gracefully** using `lui.has_errors`
4. **Iterate through elements** for multi-type responses
5. **Save important dataframes** using the `df_id` for later retrieval
6. **Check element types** before accessing type-specific properties

## Migration from Old API

If you have code using deprecated methods:

```python
# Old (doesn't work)
# df = response.to_dataframe()
# text = response.content

# New (correct)
from louieai.notebook import lui

lui("Your query")
df = lui.df          # Automatic parsing
text = lui.text      # Automatic parsing

# Or access raw elements
for element in lui.elements:
    if element.get("type") == "dataframe":
        df = element.get("table")
    elif element.get("type") == "text": 
        text = element.get("text")
```

## See Also

- [Notebook API Reference](notebook.md) - High-level cursor interface
- [Client API Reference](client.md) - Lower-level client access
- [Query Patterns Guide](../guides/query-patterns.md) - Examples of different query types