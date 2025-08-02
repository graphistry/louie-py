# Databricks Agent Guide

The Databricks agents provide powerful integration with Databricks SQL Analytics, offering both AI-assisted query generation with semantic understanding and direct SQL execution.

## Overview

- **DatabricksAgent** - AI-powered natural language to SQL with semantic layer
- **DatabricksPassthroughAgent** - Direct SQL execution without AI interpretation

## DatabricksAgent (AI-Assisted)

The DatabricksAgent understands your Databricks environment, including:
- Database schemas and table relationships
- Business terminology and metrics
- Data patterns and common queries
- Unity Catalog structure

### Basic Usage

```python
from louieai.notebook import lui

# Simple queries with business context
lui("Show me daily active users for last month", agent="DatabricksAgent")

# The agent understands your schema and generates appropriate SQL
lui("Which products have the highest return rate?", agent="DatabricksAgent")
```

### Advanced Semantic Understanding

```python
# Complex business metrics
lui("""
Calculate customer lifetime value by acquisition channel, 
including repeat purchase rate and average order value
""", agent="DatabricksAgent")

# Cross-database analytics
lui("""
Compare inventory levels with sales velocity to identify 
products at risk of stockout in the next 2 weeks
""", agent="DatabricksAgent")

# Time-series analysis
lui("""
Show me the trend of user engagement metrics with 
week-over-week and month-over-month comparisons
""", agent="DatabricksAgent")
```

### Working with Unity Catalog

```python
# Explore catalog structure
lui("Show me all tables in the analytics catalog", agent="DatabricksAgent")

# Query across catalogs
lui("""
Join customer data from prod catalog with 
marketing campaigns from analytics catalog
""", agent="DatabricksAgent")

# Schema discovery
lui("Describe the schema and relationships in the sales database", 
    agent="DatabricksAgent")
```

### Delta Lake Features

```python
# Time travel queries
lui("Show me what the revenue looked like last Tuesday", agent="DatabricksAgent")

# Version history
lui("Show me the history of changes to the customers table", agent="DatabricksAgent")

# Optimize suggestions
lui("Which tables would benefit from optimization?", agent="DatabricksAgent")
```

## DatabricksPassthroughAgent (Direct SQL)

For direct SQL execution when you know exactly what you want:

### Basic Queries

```python
# Direct SQL execution
lui("""
SELECT 
    customer_id,
    SUM(order_value) as total_revenue,
    COUNT(*) as order_count
FROM sales.orders
WHERE order_date >= '2024-01-01'
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 100
""", agent="DatabricksPassthroughAgent")

# Access the results
df = lui.df
print(f"Found {len(df)} high-value customers")
```

### Complex Analytics

```python
# Window functions and CTEs
lui("""
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        product_id,
        SUM(quantity * price) as revenue
    FROM sales.order_items
    GROUP BY 1, 2
),
ranked_products AS (
    SELECT 
        month,
        product_id,
        revenue,
        ROW_NUMBER() OVER (PARTITION BY month ORDER BY revenue DESC) as rank
    FROM monthly_sales
)
SELECT * FROM ranked_products WHERE rank <= 10
""", agent="DatabricksPassthroughAgent")
```

### Delta Lake Operations

```python
# Query specific version
lui("""
SELECT * FROM customers VERSION AS OF 5
""", agent="DatabricksPassthroughAgent")

# Time travel
lui("""
SELECT * FROM inventory TIMESTAMP AS OF '2024-01-15'
""", agent="DatabricksPassthroughAgent")

# Show table history
lui("""
DESCRIBE HISTORY sales.orders LIMIT 10
""", agent="DatabricksPassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use DatabricksAgent when:**
- You want to describe what you need in business terms
- You're exploring data and don't know the exact schema
- You need help constructing complex queries
- You want the agent to optimize query performance

**Use DatabricksPassthroughAgent when:**
- You have exact SQL you want to execute
- You're running DDL operations (CREATE, ALTER, DROP)
- You need precise control over query execution
- You're working with Databricks-specific SQL extensions

### Performance Tips

```python
# Let the AI agent optimize for you
lui("Show me the top customers but make it fast", agent="DatabricksAgent")

# Or control optimization directly
lui("""
SELECT /*+ BROADCAST(small_table) */ 
    l.*, s.* 
FROM large_table l 
JOIN small_table s ON l.id = s.id
""", agent="DatabricksPassthroughAgent")
```

### Error Handling

```python
# AI agent provides helpful error context
lui("Show me data from non_existent_table", agent="DatabricksAgent")
# Returns explanation about table not found and suggests similar tables

# Passthrough shows raw errors
lui("SELECT * FROM non_existent_table", agent="DatabricksPassthroughAgent")
# Returns actual Databricks SQL error
```

## Common Patterns

### Data Quality Checks

```python
# AI-assisted quality analysis
lui("""
Analyze data quality issues in the customer table,
including nulls, duplicates, and invalid values
""", agent="DatabricksAgent")

# Direct validation query
lui("""
SELECT 
    COUNT(*) as total_rows,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) as null_emails,
    SUM(CASE WHEN email NOT LIKE '%@%' THEN 1 ELSE 0 END) as invalid_emails
FROM customers
""", agent="DatabricksPassthroughAgent")
```

### Incremental Processing

```python
# AI helps with incremental logic
lui("""
Show me new orders since my last processing run,
assume I track this in the etl_control table
""", agent="DatabricksAgent")

# Direct incremental query
lui("""
SELECT * FROM orders 
WHERE created_at > (SELECT MAX(last_processed) FROM etl_control WHERE job_name = 'orders_etl')
""", agent="DatabricksPassthroughAgent")
```

## Integration with Other Agents

```python
# Generate SQL with Databricks agent
lui("Create a query for customer churn analysis", agent="DatabricksAgent")

# Visualize results with Graph agent
lui("Create a network graph of customer relationships", agent="GraphAgent")

# Generate Python code to process results
lui("Write Python code to calculate churn probability from this data", agent="CodeAgent")
```

## Next Steps

- Learn about [Splunk Agent](splunk.md) for log analysis
- Explore [PostgreSQL Agent](postgresql.md) for traditional databases
- See [Agent Selection Guide](../agent-selection.md) for choosing the right agent
- Check the [Query Patterns Guide](../query-patterns.md) for more examples