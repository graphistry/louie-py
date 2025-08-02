# Architecture Overview

LouieAI is built around a **thread-based conversation system** with specialized agents. The library provides both a notebook-friendly interface and a traditional client API for different use cases.

## Core Components

### 1. Thread System

LouieAI maintains conversation **threads** that preserve context across multiple queries:

```python
# Traditional client API
client = LouieClient()
response = client.add_cell(thread_id, "Analyze customer data")  # Adds to existing thread
response = client.add_cell("", "Follow-up question")           # Creates new thread

# Notebook API  
from louieai.notebook import lui
lui("Analyze customer data")  # Auto-manages thread
lui("Follow-up question")     # Continues same thread
```

### 2. Agent System

**40+ specialized agents** handle different data sources and tasks:

- **Database Agents**: PostgresAgent, MySQLAgent, SnowflakeAgent, etc.
- **Visualization Agents**: GraphAgent, PerspectiveAgent, KeplerAgent
- **Development Agents**: CodeAgent, NotebookAgent, TableAIAgent
- **Passthrough Agents**: Direct query execution without AI interpretation

### 3. Response Elements

Responses contain **structured elements** rather than raw text:

```python
response.elements = [
    {"type": "TextElement", "content": "Analysis results..."},
    {"type": "DfElement", "table": pandas_dataframe},
    {"type": "DebugLine", "text": "Debug info"},
    {"type": "ExceptionElement", "error": "Error details"}
]
```

## API Architecture

### Thread Management

When you call `client.add_cell(thread_id, prompt, agent="SomeAgent")`:

1. **Authentication**: Retrieves JWT from PyGraphistry via `graphistry.api_token()`
2. **Thread Resolution**: Creates new thread if `thread_id=""`, otherwise uses existing
3. **Agent Selection**: Routes to specified agent (defaults to LouieAgent)
4. **API Request**: POST to `/api/dthread/{thread_id}/cell` with prompt and agent
5. **Response Processing**: Parses structured response elements
6. **Error Handling**: Raises `RuntimeError` with detailed error messages

### Notebook Interface

The notebook API (`lui`) provides a streamlined interface:

```python
lui("Query")          # Returns cursor object, auto-displays in Jupyter
lui.text             # Access last response text
lui.df               # Access last response dataframe  
lui[-1].df           # Access previous response dataframe
lui.has_errors       # Check for errors
lui.errors           # List of error elements
```

### Streaming Support

Real-time response streaming in Jupyter notebooks:

- Progressive display updates as responses arrive
- Throttled updates (max 10/second) for performance
- Element-by-element rendering with appropriate styling
- Dataframe fetching via `/api/dthread/{thread_id}/df/block/{block_id}/arrow`

## Data Flow

```
User Query → Agent Selection → LouieAI API → Agent Processing → Structured Response → Element Rendering
```

1. **Input**: Natural language query with optional agent specification
2. **Routing**: Agent system routes to appropriate handler (database, visualization, etc.)
3. **Processing**: Agent processes query (SQL generation, code execution, etc.)
4. **Response**: Structured elements returned (text, dataframes, visualizations)
5. **Display**: Elements rendered appropriately (HTML, tables, graphs)

## Design Principles

### Multi-tenancy Support

- **Isolated clients**: Separate `LouieClient` instances with distinct authentication
- **Thread isolation**: Each client maintains independent conversation threads
- **No shared state**: Thread-safe for concurrent multi-user applications

### Error Handling

- **Structured errors**: Error elements included in response rather than exceptions
- **Graceful degradation**: Partial responses displayed even with some errors
- **Debug information**: DebugLine and InfoLine elements for troubleshooting

### Agent Flexibility

- **AI-assisted agents**: Natural language to query language with semantic understanding
- **Passthrough agents**: Direct execution for precise control
- **Agent composition**: Chain different agents for complex workflows

## Current API Endpoints

- **`POST /api/dthread/{thread_id}/cell`**: Add cell to thread (main query endpoint)
- **`GET /api/dthread/{thread_id}/df/block/{block_id}/arrow`**: Fetch dataframe as Arrow format
- **`POST /api/dthread/create`**: Create new thread
- **Authentication via JWT tokens from PyGraphistry**

## Integration Points

### PyGraphistry Integration

- Shares authentication tokens seamlessly
- Leverages existing PyGraphistry server configurations
- Supports multi-server deployments (hub.graphistry.com ↔ den.louie.ai)

### Jupyter Notebook Integration

- IPython.display integration for rich output
- Real-time streaming with progressive updates
- Automatic dataframe and visualization rendering
- History management with indexed access (`lui[-1]`, `lui[-2]`, etc.)