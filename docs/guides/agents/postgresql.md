# PostgreSQL Agent Guide

Access PostgreSQL databases with natural language or direct SQL.

## Overview

- **PostgresAgent** - AI-powered natural language to SQL
- **PostgresPassthroughAgent** - Direct SQL execution

## Usage Examples

```python
# AI-assisted queries with business context
lui("Show me all active customers", agent="PostgresAgent")

# Data exploration
lui("Describe the customer table and its relationships", agent="PostgresAgent")

# Direct SQL execution
lui("SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id HAVING COUNT(*) > 5", 
    agent="PostgresPassthroughAgent")

# JSON operations
lui("SELECT data->>'name' as name, data->'address'->>'city' as city FROM customers_json", 
    agent="PostgresPassthroughAgent")
```

## Common Patterns

- Customer analytics
- Data quality analysis
- Transaction management
- Performance optimization

## Integration

Query with PostgresAgent, then visualize with GraphAgent or analyze with CodeAgent.