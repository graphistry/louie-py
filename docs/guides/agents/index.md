# Agent Guides

Detailed guides for using LouieAI's specialized agents. Each agent type has two variants:

- **AI-Assisted** - Natural language interface with semantic understanding
- **Passthrough** - Direct execution without AI interpretation

## Database Agents

### [Databricks Agent](databricks.md)
Powerful integration with Databricks SQL Analytics, Unity Catalog, and Delta Lake.
- AI understands your schemas and business metrics
- Natural language to optimized SQL
- Direct SQL execution option

### [PostgreSQL Agent](postgresql.md)
Comprehensive PostgreSQL support with semantic layer.
- Complex business logic understanding
- Query optimization suggestions
- Full SQL control when needed

### [Splunk Agent](splunk.md)
Advanced log analysis and security monitoring.
- Natural language to SPL queries
- Pattern recognition and anomaly detection
- Direct SPL execution

## Analytics & Visualization

### [Graph Agent](graph.md)
Network visualization using Graphistry.
- AI-powered graph generation from descriptions
- Automatic layout and styling
- Direct graph specification with JSON

### [Python Code Agent](code.md)
Generate and execute Python code for data processing.
- Complete data science workflows
- Best practices and error handling
- Direct code execution

## Quick Comparison

| Use Case | AI-Assisted Agent | Passthrough Agent |
|----------|------------------|-------------------|
| **Exploring data** | ✅ Best choice - describes what you need | ❌ Requires knowing structure |
| **Complex queries** | ✅ Handles joins and logic automatically | ⚠️ Must write manually |
| **Exact control** | ⚠️ May interpret differently | ✅ Executes exactly as written |
| **Learning curve** | ✅ Natural language | ❌ Need to know query language |
| **Performance** | ✅ Often optimizes queries | ✅ Full control over execution |

## Common Patterns

### Multi-Agent Workflows

```python
# 1. Explore with database agent
lui("Show me customer behavior patterns", agent="PostgresAgent")

# 2. Visualize findings
lui("Create a network of customer interactions", agent="GraphAgent")

# 3. Generate analysis code
lui("Write code to predict customer churn", agent="CodeAgent")

# 4. Monitor in production
lui("Create Splunk queries to track model performance", agent="SplunkAgent")
```

### Choosing Between AI and Passthrough

```python
# Use AI when exploring
lui("Find security anomalies in the logs", agent="SplunkAgent")

# Use passthrough when you know exactly what you want
lui('index=security event_type="failed_login" | stats count by src_ip', 
    agent="SplunkPassthroughAgent")
```

## More Agents

See the [complete agents reference](../../reference/agents.md) for all 40+ available agents including:

- **SQL Databases**: MySQL, MSSQL, Snowflake, BigQuery
- **NoSQL**: OpenSearch, Neptune (Graph DB)
- **Visualization**: Kepler (Maps), Perspective (Tables), Mermaid (Diagrams)
- **Specialized**: Firecrawl (Web scraping), Recipe/Example management

## Getting Started

1. Start with the AI-assisted version to explore your data
2. Review the generated queries to understand patterns
3. Switch to passthrough agents when you need exact control
4. Combine multiple agents for complex workflows

Each guide includes:
- ✅ Real-world examples
- ✅ Best practices
- ✅ Performance tips
- ✅ Integration patterns