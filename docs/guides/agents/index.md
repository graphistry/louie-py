# Agent Guide

LouieAI provides 40+ specialized agents for different data sources and tasks. Each agent is designed for specific use cases and data types, with most offering two variants:

- **AI-Assisted** (e.g., `PostgresAgent`) - Natural language to query language with semantic understanding
- **Passthrough** (e.g., `PostgresPassthroughAgent`) - Direct query execution without AI interpretation

Agent names are exact and checked by the server: an unknown name fails with `400 Bad Request` and the detail `Invalid agent '<name>'`. Most names end in `Agent`; the exceptions are `Splunk` / `SplunkPassthrough`, `Kusto` / `KustoPassthrough`, and `NotebookTool`.

## Availability

Which agents you can use depends on your Louie deployment:

- **Data source agents** (databases, Splunk, Kusto, OpenSearch, ...) query the connections configured for your Louie organization or server.
- **Louie Desktop** does not include the SQL agents (Postgres, MySQL, MSSQL, BigQuery, CockroachDB), Spanner, Neptune, or TableAI. Use a Louie server (Louie Web or self-hosted) for those.
- **Server features** such as web search, notebook editing, and maps (`KeplerAgent` needs a map tile source configured on the server) are turned on by the server's administrator.

## Agent Types

### General Purpose Agents
- **LouieAgent** (default) - General conversational AI for analysis and mixed tasks
- **TextAgent** - Basic text processing and manipulation
- **DoNothingAgent** - Testing agent that returns empty responses

### Database Query Agents with Semantic Layer
Database agents build **semantic understanding** of your data:
- **Schema Discovery**: Learn database structure and relationships automatically
- **Semantic Modeling**: Understand business context and domain terminology  
- **Intelligent Query Generation**: Generate queries based on meaning, not keywords
- **Cross-Table Reasoning**: Infer joins and relationships automatically

## How to Use Agents

### Notebook API
```python
from louieai.notebook import lui

# Default general-purpose agent
lui("Analyze customer behavior patterns")

# Specify database agent
lui("Show failed login attempts from last hour", agent="Splunk")

# Use passthrough for exact SQL
lui("SELECT * FROM logs LIMIT 10", agent="PostgresPassthroughAgent")
```

### Traditional Client API
```python
from louieai import LouieClient
client = LouieClient()

# With agent parameter
response = client.add_cell("", "Analyze patterns", agent="LouieAgent")
response = client.add_cell("", "SELECT * FROM events", agent="PostgresPassthroughAgent")
```

### Code & Notebook Agents
- **CodeAgent** - AI-powered Python code generation with explanations
- **CodePassthroughAgent** - Direct Python code execution without AI interpretation
- **NotebookTool** - List, read, and copy between your Louie notebooks; edits and runs cells when the server enables notebook editing

### Data Visualization Agents
- **GraphAgent** / **GraphPassthroughAgent** - Network graphs with Graphistry
- **PerspectiveAgent** / **PerspectivePassthroughAgent** - Interactive data tables
- **MermaidAgent** / **MermaidPassthroughAgent** - Flowcharts and diagrams
- **KeplerAgent** - Interactive geospatial maps

### Specialized Agents
- **TableAIAgent** - AI-powered table analysis and insights  
- **Web search & scraping** - No `agent=` needed: when web search is enabled on your Louie server, the default `LouieAgent` routes to it (Firecrawl is one of its providers)

## Quick Reference Table

| **Data Source** | **Agent** | **Use Cases** | **Query Language** |
|---|---|---|---|
| **Cloud Data Warehouses** |
| BigQuery | `BigQueryAgent` | Petabyte analytics, ML, geospatial | SQL |
| Databricks | `DatabricksAgent` | Unity Catalog, Delta Lake | SQL |
| **Traditional Databases** |
| PostgreSQL | `PostgresAgent` | OLTP/Analytics, JSON, advanced features | SQL |
| MySQL | `MySQLAgent` | Web applications, performance optimization | SQL |
| SQL Server | `MSSQLAgent` | Enterprise Windows environments | T-SQL |
| **Distributed Systems** |
| CockroachDB | `CockroachDBAgent` | Global consistency, multi-region | SQL |
| Spanner | `SpannerAgent` | Global scale, strong consistency | SQL |
| **Search & Logs** |
| OpenSearch | `OpenSearchAgent` | Log analytics, security monitoring | Query DSL |
| Splunk | `Splunk` | Security operations, correlations | SPL |
| Kusto | `Kusto` | Azure telemetry, time series | KQL |
| **Graph Databases** |
| Neptune | `NeptuneAgent` | Relationship analysis | Cypher |
| **Visualization** |
| Graph | `GraphAgent` | Network analysis with Graphistry | JSON |
| Kepler | `KeplerAgent` | Geospatial mapping | Config |
| Perspective | `PerspectiveAgent` | Interactive data tables | Config |
| Mermaid | `MermaidAgent` | Diagrams and flowcharts | Mermaid |
| **Development** |
| Code | `CodeAgent` | Python data processing | Python |
| Notebook | `NotebookTool` | Reuse earlier Louie notebooks; edit cells when enabled | Natural Language |
| TableAI | `TableAIAgent` | Intelligent data insights | Natural Language |
| **Data Collection** |
| Web pages | `LouieAgent` (default; needs web search enabled) | Web search, scraping | Natural Language |

## Semantic Understanding Example

Database agents leverage semantic understanding for intelligent queries:

```python
# Natural language query
lui("Show me customer churn trends", agent="DatabricksAgent")

# The agent automatically:
# - Maps "customer churn" to relevant tables/columns
# - Calculates appropriate time periods
# - Determines necessary joins and aggregations
# - Applies business logic and definitions
```

## AI vs Passthrough Comparison

| Use Case | AI-Assisted Agent | Passthrough Agent |
|----------|------------------|-------------------|
| **Exploring data** | ✅ Best choice - describes what you need | ❌ Requires knowing structure |
| **Complex queries** | ✅ Handles joins and logic automatically | ⚠️ Must write manually |
| **Exact control** | ⚠️ May interpret differently | ✅ Executes exactly as written |
| **Learning curve** | ✅ Natural language | ❌ Need to know query language |
| **Performance** | ✅ Often optimizes queries | ✅ Full control over execution |

## Agent Selection Guidelines

### When to Use AI-Assisted Agents
- **Exploring new data sources** - "Show me customer behavior patterns"
- **Complex business questions** - "Find high-risk transactions across regions"
- **Learning query patterns** - See how the AI structures queries for your use case

### When to Use Passthrough Agents  
- **Exact control needed** - Specific SQL optimizations or edge cases
- **Known query patterns** - You already know the exact query to run
- **Performance critical** - Direct execution without AI processing overhead

### Multi-Agent Workflows

```python
# 1. Explore with database agent
lui("Show me customer behavior patterns", agent="PostgresAgent")

# 2. Visualize findings  
lui("Create a network of customer interactions", agent="GraphAgent")

# 3. Generate analysis code
lui("Write code to predict customer churn", agent="CodeAgent")

# 4. Monitor in production
lui("Create Splunk queries to track model performance", agent="Splunk")
```

## Individual Agent Guides

**Database Agents:**
- [Databricks](databricks.md) - Unity Catalog, Delta Lake analytics
- [PostgreSQL](postgresql.md) - Advanced SQL features, JSON support
- [Splunk](splunk.md) - Security operations, log analysis
- [BigQuery](bigquery.md) - Petabyte analytics, ML integration
- [MySQL](mysql.md) - Web application databases
- [OpenSearch](opensearch.md) - Search and log analytics
- [CockroachDB](cockroachdb.md), [Kusto](kusto.md), [MSSQL](mssql.md), [Neptune](neptune.md), [Spanner](spanner.md)

**Visualization Agents:**
- [Graph](graph.md) - Network visualization with Graphistry
- [Kepler](kepler.md) - Geospatial mapping
- [Perspective](perspective.md) - Interactive data tables
- [Mermaid](mermaid.md) - Diagrams and flowcharts

**Development Agents:**
- [Code](code.md) - Python code generation
- [Notebook](notebook.md) - Reuse earlier Louie notebooks; edit cells when enabled
- [TableAI](tableai.md) - Intelligent data insights
- [Web Scraping](firecrawl.md) - Via the default `LouieAgent` (Firecrawl and other providers)