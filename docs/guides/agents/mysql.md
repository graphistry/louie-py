# MySQL Agent Guide

Access MySQL and MariaDB databases with natural language or direct SQL.

## Overview

- **MySQLAgent** - AI-powered natural language to SQL
- **MySQLPassthroughAgent** - Direct SQL execution

## Usage Examples

```python
# AI-assisted queries with business context
lui("Show me our top customers by revenue", agent="MySQLAgent")

# Performance analysis  
lui("Which queries are causing table locks?", agent="MySQLAgent")

# Direct SQL execution
lui("SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id HAVING COUNT(*) > 10", 
    agent="MySQLPassthroughAgent")

# JSON operations (MySQL 5.7+)
lui("SELECT JSON_EXTRACT(metadata, '$.source') FROM orders WHERE created_date >= CURDATE()", 
    agent="MySQLPassthroughAgent")
```

## Common Patterns

- E-commerce analytics
- Performance optimization
- Data quality checks
- Full-text search

## Integration

Query with MySQLAgent, then process results with CodeAgent or create visualizations with PerspectiveAgent.