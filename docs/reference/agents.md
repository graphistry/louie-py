# Available Agents Reference

This page lists all available agent types in LouieAI. Each agent is specialized for different tasks and data sources.

## General Purpose Agents

### Conversational & Text Processing
- **LouieAgent** (default) - General conversational AI agent for analysis, queries, and mixed tasks
- **TextAgent** - Basic text processing and manipulation
- **DoNothingAgent** - Testing agent that returns empty responses

### Code & Notebook Agents
- **CodeAgent** - AI-powered Python code generation with explanations
- **CodePassthroughAgent** - Direct Python code execution without AI interpretation
- **NotebookAgent** - Jupyter notebook cell operations and management

## Data Visualization Agents

### Graph Visualization
- **GraphAgent** - Network graph visualization with AI-assisted layout and styling
- **GraphPassthroughAgent** - Direct graph visualization from JSON specification
- **GraphUMAPPassthroughAgent** - Graph visualization with UMAP dimensionality reduction layout

### Charts & Diagrams
- **PerspectiveAgent** - Interactive data tables and charts with AI assistance
- **PerspectivePassthroughAgent** - Direct Perspective.js table configuration
- **MermaidAgent** - Flowcharts and diagrams using Mermaid syntax with AI help
- **MermaidPassthroughAgent** - Direct Mermaid diagram syntax input

### Geospatial
- **KeplerAgent** - Interactive map visualizations using Kepler.gl

### Table Analysis
- **TableAIAgent** - AI-powered table analysis and insights

## Database Query Agents

### Semantic Layer & Schema Learning

Database agents in LouieAI do more than simple query generation - they build a **semantic understanding** of your data:

1. **Schema Discovery**: Agents automatically learn your database schema, table relationships, and data types
2. **Semantic Modeling**: They understand business context, common patterns, and domain-specific terminology
3. **Intelligent Query Generation**: Queries are generated based on semantic understanding, not just keyword matching
4. **Cross-Table Reasoning**: Agents can infer joins and relationships even when not explicitly stated

Example of semantic understanding:
```python
# Instead of needing to specify tables and joins:
lui("Show me customer churn last quarter", agent="DatabricksAgent")

# The agent understands:
# - "customer churn" maps to specific tables/columns
# - "last quarter" needs date range calculation
# - Required joins between customer, subscription, and date tables
# - Appropriate aggregations and filters
```

### Agent Variants

Each database type has two variants:
- **[Database]Agent** - AI-powered with semantic understanding and natural language interface
- **[Database]PassthroughAgent** - Direct query execution without AI interpretation

### Analytics Databases
- **DatabricksAgent** / **DatabricksPassthroughAgent** - Databricks SQL Analytics
- **SnowflakeAgent** / **SnowflakePassthroughAgent** - Snowflake data warehouse
- **BigQueryAgent** / **BigQueryPassthroughAgent** - Google BigQuery
- **AthenaAgent** / **AthenaPassthroughAgent** - AWS Athena

### Search & Log Analytics
- **OpenSearchAgent** / **OpenSearchPassthroughAgent** - OpenSearch queries
- **SplunkAgent** / **SplunkPassthroughAgent** - Splunk SPL queries
- **KustoAgent** / **KustoPassthroughAgent** - Azure Data Explorer (KQL)

### Traditional SQL Databases
- **PostgresAgent** / **PostgresPassthroughAgent** - PostgreSQL databases
- **MySQLAgent** / **MySQLPassthroughAgent** - MySQL/MariaDB databases
- **MSSQLAgent** / **MSSQLPassthroughAgent** - Microsoft SQL Server
- **CockroachDBAgent** / **CockroachDBPassthroughAgent** - CockroachDB

### Graph Databases
- **NeptuneAgent** / **NeptunePassthroughAgent** - AWS Neptune (Cypher queries)

### Other Databases
- **SpannerAgent** / **SpannerPassthroughAgent** - Google Cloud Spanner

## Specialized Agents

### Web & Data Collection
- **FirecrawlAgent** - Web scraping and data extraction from websites

### Recipe Management
- **RecipeListOrgAgent** - List organization-level saved queries
- **RecipeSaveOrgAgent** - Save queries at organization level
- **RecipeListSystemAgent** - List system-level saved queries
- **RecipeSaveSystemAgent** - Save queries at system level

### Example Management
- **ExampleListOrgAgent** - List organization examples
- **ExampleSaveOrgAgent** - Save organization examples
- **ExampleDeleteOrgAgent** - Delete organization examples
- **ExampleListSystemAgent** - List system examples
- **ExampleSaveSystemAgent** - Save system examples
- **ExampleDeleteSystemAgent** - Delete system examples

## Usage Examples

### Basic Usage
```python
# Default agent (LouieAgent)
lui("Analyze the security logs")

# Specify a different agent
lui("SELECT * FROM events WHERE severity='HIGH'", agent="SplunkPassthroughAgent")
```

### AI-Assisted vs Passthrough

**AI-Assisted Agents** leverage semantic understanding:
```python
# Natural language with business context
lui("Show me suspicious user behavior patterns", agent="PostgresAgent")
# Agent understands:
# - What constitutes "suspicious" in your data model
# - Which tables contain user behavior data
# - Appropriate time windows and thresholds
# - Complex joins and aggregations needed

# Another example with learned semantics
lui("Compare this month's revenue to last month by product category", agent="DatabricksAgent")
# Agent knows:
# - Revenue calculation from your specific schema
# - Product hierarchy and categorization
# - Proper date handling for your fiscal calendar
```

**Passthrough Agents** for direct control:
```python
# When you know exactly what you want
lui("SELECT * FROM auth_logs WHERE status='failed'", agent="PostgresPassthroughAgent")
# Executes exactly as written - no interpretation
```

### Visualization Agents
```python
# AI-assisted graph creation
lui("Create a network showing user connections", agent="GraphAgent")

# Direct graph specification
graph_json = {"nodes": [...], "edges": [...]}
lui(json.dumps(graph_json), agent="GraphPassthroughAgent")
```

## Agent Selection Best Practices

1. **Use the default LouieAgent** for:
   - General analysis and questions
   - Mixed queries requiring multiple steps
   - When you're unsure which agent to use

2. **Use specialized database agents** when:
   - Working with specific data sources (e.g., DatabricksAgent for Databricks)
   - You want the agent to leverage learned semantic understanding of your schema
   - You prefer natural language over writing SQL
   - You need complex queries involving multiple tables and business logic

3. **Benefits of semantic layer**:
   - **Faster query development**: Describe what you want, not how to get it
   - **Consistent business logic**: Agents learn and apply your organization's definitions
   - **Reduced errors**: Semantic understanding prevents common SQL mistakes
   - **Knowledge sharing**: New users can query without knowing the schema

3. **Use passthrough agents** when:
   - You have exact queries/specifications
   - You want to avoid AI interpretation
   - Performance is critical

4. **Combine agents** for complex workflows:
   ```python
   # Step 1: Generate SQL with AI
   lui("Find suspicious transactions", agent="PostgresAgent")
   
   # Step 2: Visualize results
   lui("Create a graph of these transactions", agent="GraphAgent")
   
   # Step 3: General analysis
   lui("What patterns do you see?", agent="LouieAgent")
   ```

## Notes

- Agent availability depends on your Louie deployment and configured data sources
- Some agents require specific permissions or data source connections
- Agent names are case-sensitive (use exact names as shown)
- The default LouieAgent can handle most queries effectively

For implementation details, see the [Agent Selection Guide](../guides/agent-selection.md).