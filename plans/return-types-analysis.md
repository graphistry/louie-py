# Louie.ai Return Types Analysis

## Overview

Based on analysis of `graphistrygpt/models/`, Louie.ai can return various element types in responses. The Python client needs to handle these appropriately to give users access to all returned data.

## Core Element Types

### 1. TextElement
- **Type**: `TextElement`
- **Purpose**: Natural language responses, code snippets, markdown content
- **Key Fields**:
  - `text`: The content string
  - `language`: Language type (Markdown, JSON, Python, etc.)
- **Usage Example**:
  ```python
  # User asks for explanation
  response = client.add_cell(thread.id, "Explain the data patterns")
  # Returns TextElement with markdown explanation
  print(response.content)  # Natural language explanation
  ```

### 2. DfElement / DfElementFlat
- **Type**: `DfElement` (full) or `DfElementFlat` (serialized)
- **Purpose**: DataFrame results from queries
- **Key Fields**:
  - `df`: The pandas DataFrame (in DfElement)
  - `metadata`: FrontEndDf with summary info
  - `version`: Version number for updates
- **Usage Example**:
  ```python
  # User queries database
  response = client.add_cell(thread.id, "Query PostgreSQL sales table")
  df = response.to_dataframe()  # Extracts pandas DataFrame
  ```

### 3. GraphElement / GraphElementFlat
- **Type**: `GraphElement` (full) or `GraphElementFlat` (serialized)
- **Purpose**: Graphistry visualization results
- **Key Fields**:
  - `dataset_id`: ID for the Graphistry visualization
  - `g`: GraphistryPydantic object (optional)
  - `status`: Status of visualization creation
  - `params`: Visualization parameters
- **Usage Example**:
  ```python
  # User requests graph visualization
  response = client.add_cell(thread.id, "Visualize user connections in Graphistry")
  # Returns GraphElement with dataset_id
  graph_url = f"https://hub.graphistry.com/graph/graph.html?dataset={response.dataset_id}"
  ```

### 4. KeplerElement
- **Type**: `KeplerElement`
- **Purpose**: Kepler.gl map visualizations
- **Key Fields**:
  - `title`: Map title
  - `data_refs`: References to data elements
  - `config`: KeplerConfig with map settings
- **Usage Example**:
  ```python
  # User requests geographic visualization
  response = client.add_cell(thread.id, "Create Kepler map of customer locations")
  # Returns KeplerElement with map configuration
  ```

### 5. PerspectiveElement
- **Type**: `PerspectiveElement`
- **Purpose**: Perspective charts (heatmaps, pivots, etc.)
- **Key Fields**:
  - `df_element_id`: Reference to data
  - `config`: PerspectiveConfig with chart settings
- **Usage Example**:
  ```python
  # User requests chart
  response = client.add_cell(thread.id, "Create heatmap of sales by region and month")
  # Returns PerspectiveElement with chart config
  ```

### 6. ExceptionElement
- **Type**: `ExceptionElement`
- **Purpose**: Error information
- **Key Fields**:
  - `text`: Error message
  - `traceback`: Optional stack trace
- **Usage Example**:
  ```python
  # When query fails
  response = client.add_cell(thread.id, "Query non-existent table")
  if response.type == "ExceptionElement":
      print(f"Error: {response.text}")
  ```

### 7. Base64ImageElement
- **Type**: `Base64ImageElement`
- **Purpose**: Generated images (matplotlib, seaborn, etc.)
- **Key Fields**:
  - `src`: Base64 encoded image data
  - `props`: Image properties
  - `height`, `width`: Dimensions
- **Usage Example**:
  ```python
  # User requests chart
  response = client.add_cell(thread.id, "Plot sales trend with matplotlib")
  # Returns Base64ImageElement
  # Can be displayed in Jupyter or saved to file
  ```

### 8. CallElement
- **Type**: `CallElement`
- **Purpose**: Record of agent/tool calls
- **Key Fields**:
  - `agent`: Agent type that was called
  - `text`: Call details
  - `language`: Usually Python
  - `run_id`: Execution ID

### 9. InputGroupElement
- **Type**: `InputGroupElement`
- **Purpose**: Interactive input forms
- **Key Fields**:
  - `items`: List of input items
- **Note**: Primarily for UI, less relevant for API client

## Response Structures

### Single Element Response
Most queries return a single primary element:
```python
response = client.add_cell(thread.id, "Query database")
# response might contain one DfElement
```

### Multi-Element Response
Complex queries can return multiple elements:
```python
response = client.add_cell(thread.id, """
    Query sales data, create UMAP visualization, 
    and provide summary insights
""")
# response might contain:
# - DfElement with query results
# - GraphElement with UMAP visualization
# - TextElement with insights
```

### Element Union Types
The code defines union types for handling multiple element types:
- `ElementUnion`: All possible element types
- `ElementUnionFlat`: Serialized versions for transport

## Documentation Recommendations

### 1. Response Type Detection
Document how to detect response type:
```python
def handle_response(response):
    if hasattr(response, 'to_dataframe') and response.to_dataframe() is not None:
        # Handle DataFrame response
        df = response.to_dataframe()
    elif hasattr(response, 'dataset_id'):
        # Handle Graphistry visualization
        url = build_graphistry_url(response.dataset_id)
    elif hasattr(response, 'text'):
        # Handle text/markdown response
        content = response.text
```

### 2. Multi-Element Handling
Show how to handle responses with multiple elements:
```python
def process_multi_element_response(response):
    elements = response.elements  # hypothetical API
    
    dataframes = [e for e in elements if e.type == "DfElement"]
    visualizations = [e for e in elements if e.type in ["GraphElement", "KeplerElement"]]
    insights = [e for e in elements if e.type == "TextElement"]
```

### 3. Error Handling
Clear patterns for error detection:
```python
def safe_query(client, thread_id, query):
    response = client.add_cell(thread_id, query)
    
    if response.type == "ExceptionElement":
        raise RuntimeError(f"Query failed: {response.text}")
    
    return response
```

### 4. Visualization URL Construction
Helper functions for visualization access:
```python
def get_visualization_url(element):
    if element.type == "GraphElement":
        return f"https://hub.graphistry.com/graph/graph.html?dataset={element.dataset_id}"
    elif element.type == "KeplerElement":
        # Return Kepler URL or config
        return element.config
    # etc.
```

## Key Insights for V1 Client

1. **Core Response Types**: Focus on TextElement, DfElement, and GraphElement as most common
2. **Simple API**: Client doesn't need methods for each element type - Louie returns appropriate type based on query
3. **Type Detection**: Provide clear examples of detecting and handling different response types
4. **Future-Proof**: Document that new element types may be added as Louie evolves

## Implementation Notes

- The Python client should provide convenient accessors for common operations:
  - `.to_dataframe()` for DfElement responses
  - `.content` or `.text` for TextElement responses  
  - `.visualization_url` for GraphElement responses
  - `.error` for ExceptionElement responses

- Consider providing a `.type` property to help users identify response type programmatically

- Multi-element responses might need special handling - verify with engineering how these are returned in practice