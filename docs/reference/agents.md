# Agent Reference

This reference provides technical details about all available LouieAI agents.

## Database Agents

### Athena
- **Availability**: not enabled on current Louie servers (the agent names are accepted, but calls return no output)
- **Purpose**: Query AWS Athena databases
- **Capabilities**: SQL queries, partitioned data, S3-backed tables
- **Authentication**: AWS credentials required
- **Output**: Tabular data, query metadata

### BigQuery
- **Purpose**: Query Google BigQuery datasets
- **Capabilities**: Standard SQL, nested data, array functions
- **Authentication**: GCP service account
- **Output**: Tabular data, query statistics

### Snowflake
- **Availability**: not enabled on current Louie servers (the agent names are accepted, but calls return no output)
- **Purpose**: Query Snowflake data warehouses
- **Capabilities**: SQL queries, semi-structured data, time travel
- **Authentication**: Username/password or key-pair
- **Output**: Tabular data, query history

### PostgreSQL
- **Purpose**: Query PostgreSQL databases
- **Capabilities**: Full SQL, extensions, JSON operations
- **Authentication**: Connection string
- **Output**: Tabular data, query plans

### MySQL
- **Purpose**: Query MySQL databases
- **Capabilities**: SQL queries, stored procedures
- **Authentication**: Connection string
- **Output**: Tabular data

### Additional Database Agents
- **CockroachDB**: Distributed SQL database
- **Databricks**: Unified analytics platform
- **Kusto**: Azure Data Explorer queries
- **MSSQL**: Microsoft SQL Server
- **Neptune**: AWS graph database
- **OpenSearch**: Search and analytics
- **Spanner**: Google Cloud Spanner
- **Splunk**: Log analysis platform

## Data Visualization Agents

### Graph
- **Purpose**: Create network visualizations
- **Capabilities**: 
  - Interactive graph exploration
  - Force-directed layouts
  - Node/edge styling
  - GPU-accelerated rendering
- **Output**: Interactive Graphistry visualization

### Perspective
- **Purpose**: Create interactive data tables and charts
- **Capabilities**:
  - Pivot tables
  - Aggregations
  - Real-time updates
  - Multiple chart types
- **Output**: Interactive Perspective widget

### Kepler
- **Purpose**: Geospatial visualization
- **Capabilities**:
  - Map layers
  - Heatmaps
  - Arc/line visualizations
  - 3D terrain
- **Output**: Interactive Kepler.gl map

### Mermaid
- **Purpose**: Create diagrams and flowcharts
- **Capabilities**:
  - Flowcharts
  - Sequence diagrams
  - Gantt charts
  - Entity relationships
- **Output**: Mermaid diagram specification

## Code Execution Agents

### Code
- **Purpose**: Generate and execute Python code
- **Capabilities**:
  - Data analysis with pandas
  - Statistical computations
  - Custom algorithms
  - Library imports
- **Output**: Code output, variables, plots

### Notebook
- **Purpose**: List, read, and copy between your Louie notebooks (`NotebookTool`); creating and editing cells needs server-side enablement
- **Capabilities**:
  - List and read notebooks
  - Copy results between notebooks
  - Search run history
- **Output**: Notebook contents, tables, and summaries

## Data Processing Agents

### TableAI
- **Purpose**: Advanced table operations
- **Capabilities**:
  - Intelligent joins
  - Data cleaning
  - Feature engineering
  - Anomaly detection
- **Output**: Transformed datasets

### Web Scraping (Firecrawl)
- **Purpose**: Web search and page extraction, through the default `LouieAgent` (no `agent=`), when web search is enabled on the server
- **Capabilities**:
  - Search and fetch pages as text and links
  - Multi-page crawls (Firecrawl caps a crawl at 50 pages)
  - Data extraction
- **Output**: Structured web data

## Agent Composition

Agents can work together in workflows:

```python
# Database → Code → Visualization pipeline
lui("""
Query sales data from BigQuery,
calculate monthly trends with Python,
then create an interactive dashboard
""")
```

## Performance Characteristics

| Agent Type | Latency | Data Volume | Interactivity |
|------------|---------|-------------|---------------|
| Database   | Low-Med | High        | Query-based   |
| Visualization | Low  | Medium      | High          |
| Code       | Medium  | Medium      | Moderate      |
| Processing | High    | High        | Low           |

## Error Handling

All agents provide structured error information:
- Error type and message
- Relevant context
- Suggested fixes
- Fallback options

## See Also
- [Agent Selection](../guides/agent-selection.md) - Choosing the right agent
- [Agent Guides](../guides/agents/index.md) - Detailed usage guides
- [API Reference](../api/index.md) - Programming interface