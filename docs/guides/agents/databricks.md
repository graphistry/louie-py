# Databricks Agent Guide

Access Databricks SQL Analytics with natural language or direct SQL.

## Overview

- **DatabricksAgent** - AI-powered natural language to SQL  
- **DatabricksPassthroughAgent** - Direct SQL execution

## Usage Examples

```python
# AI-assisted queries with business context
lui("Show me daily active users for last month", agent="DatabricksAgent")

# Cross-database analytics
lui("Compare inventory levels with sales velocity", agent="DatabricksAgent")

# Direct SQL execution
lui("SELECT customer_id, SUM(order_value) FROM sales.orders GROUP BY customer_id", 
    agent="DatabricksPassthroughAgent")

# Delta Lake time travel
lui("SELECT * FROM customers VERSION AS OF 5", 
    agent="DatabricksPassthroughAgent")
```

## Common Patterns

- Customer analytics
- Real-time dashboards
- Data quality checks
- Delta Lake operations

## Integration

Query with DatabricksAgent, then visualize with GraphAgent or analyze with CodeAgent.