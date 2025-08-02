# Agent Selection Guide

LouieAI supports different agents for specialized tasks. By default, queries use the `LouieAgent`, but you can specify other agents when needed.

For a complete list of all available agents, see the [Agents Reference](../reference/agents.md).

## How to Specify an Agent

### Notebook API

```python
from louieai.notebook import lui

# Using the default LouieAgent
lui("Analyze the security logs")

# Explicitly specify an agent
lui("SELECT * FROM logs LIMIT 10", agent="PassthroughAgent")

# Use Databricks agent for SQL generation
lui("Show me failed login attempts from the last hour", agent="DatabricksAgent")
```

### Traditional Client API

```python
from louieai import LouieClient

client = LouieClient()

# Default agent
response = client.add_cell("", "Analyze patterns", agent="LouieAgent")

# Specific agent
response = client.add_cell("", "SELECT * FROM events", agent="PassthroughAgent")

# Using the callable interface
response = client("Complex SQL analysis", agent="DatabricksAgent")
```

### Factory Function with Agent

```python
import louieai

# Create a cursor
lui = louieai()

# Use different agents for different queries
lui("General analysis")  # Uses LouieAgent by default
lui("SQL: SELECT * FROM table", agent="PassthroughAgent")
lui("Generate SQL for user activity", agent="DatabricksAgent")
```

## Agent-Specific Features

### PassthroughAgent

Direct SQL execution without AI interpretation:

```python
# Prefix with "SQL:" for clarity (optional but recommended)
lui("SQL: SELECT COUNT(*) FROM security_events WHERE severity = 'HIGH'", 
    agent="PassthroughAgent")

# Results come back as dataframe directly
df = lui.df
```

### DatabricksAgent

Optimized for Databricks environments with schema awareness:

```python
# Natural language to SQL
lui("Show me all tables in the security database", agent="DatabricksAgent")

# Complex analytical queries
lui("Calculate the average response time by incident type for last month", 
    agent="DatabricksAgent")
```

### LouieAgent (Default)

General-purpose agent with full capabilities:

```python
# Mixed analysis - text, data, and visualizations
lui("Analyze security trends and create a summary report")

# Multi-step reasoning
lui("Find correlations between failed logins and geographic locations")
```

## Setting a Default Agent

If you frequently use a specific agent, you can set it as default:

```python
# Method 1: Create a wrapper
def databricks_lui(query, **kwargs):
    return lui(query, agent="DatabricksAgent", **kwargs)

# Use it
databricks_lui("Show all user tables")

# Method 2: Partial function
from functools import partial
db_query = partial(lui, agent="DatabricksAgent")
db_query("List all indexes")

# Method 3: Custom cursor (advanced)
class DatabricksCursor:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def __call__(self, query, **kwargs):
        kwargs.setdefault('agent', 'DatabricksAgent')
        return self.cursor(query, **kwargs)

db_lui = DatabricksCursor(lui)
db_lui("Analyze table statistics")
```

## Agent Selection Best Practices

1. **Use the default LouieAgent** for general analysis and mixed queries
2. **Use PassthroughAgent** when you have exact SQL and don't need AI interpretation
3. **Use DatabricksAgent** for Databricks-specific features and optimized SQL generation
4. **Be explicit** when switching between agents to avoid confusion

## Example: Multi-Agent Workflow

```python
# 1. Use Databricks agent to explore schema
lui("Show me all security-related tables", agent="DatabricksAgent")

# 2. Use passthrough for specific query
lui("SQL: SELECT * FROM security.incidents WHERE date = CURRENT_DATE", 
    agent="PassthroughAgent")
incident_df = lui.df

# 3. Use default agent for analysis
lui("Analyze these incidents and identify patterns")
print(lui.text)

# 4. Generate visualization query with Databricks agent
lui("Create a query to visualize incident trends by category", 
    agent="DatabricksAgent")
```

## Common Agents Quick Reference

The most commonly used agents:

- **LouieAgent** (default) - General conversational AI agent
- **DatabricksAgent** - Databricks SQL with schema awareness
- **SplunkAgent** - Splunk query generation and analysis
- **GraphAgent** - Network visualization with AI assistance
- **CodeAgent** - Python code generation
- **PostgresAgent** - PostgreSQL queries

See the [Agents Reference](../reference/agents.md) for the complete list of 40+ available agents.

## Checking Available Agents

To see which agents are available in your Louie instance:

```python
# Ask Louie about available agents
lui("What agents are available for queries?")

# Or check documentation for your specific deployment
```

## Notes

- Agent names are case-sensitive (use exact names like "LouieAgent", not "louieagent")
- Available agents depend on your Louie deployment configuration
- Some agents may require specific permissions or data access
- The default agent can handle most queries effectively

For more examples, see the [Query Patterns Guide](query-patterns.md).