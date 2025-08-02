# PostgreSQL Agent Guide

The PostgreSQL agents provide comprehensive database interaction capabilities with semantic understanding of your schema and business logic.

## Overview

- **PostgresAgent** - AI-powered natural language to SQL with semantic layer
- **PostgresPassthroughAgent** - Direct SQL execution without AI interpretation

## PostgresAgent (AI-Assisted)

The PostgresAgent builds semantic understanding of:
- Your database schema and relationships
- Business terminology and metrics
- Common query patterns
- Performance optimization opportunities

### Basic Usage

```python
from louieai.notebook import lui

# Simple business queries
lui("Show me all active customers", agent="PostgresAgent")

# Aggregations and analytics
lui("What's our monthly revenue trend for this year?", agent="PostgresAgent")

# Data exploration
lui("Describe the customer table and its relationships", agent="PostgresAgent")
```

### Complex Business Logic

```python
# Customer analytics
lui("""
Find customers at risk of churning based on 
decreased order frequency and support tickets
""", agent="PostgresAgent")

# Financial calculations
lui("""
Calculate the customer lifetime value including
average order value, purchase frequency, and retention rate
""", agent="PostgresAgent")

# Inventory management
lui("""
Show products that need reordering based on current stock,
lead time, and average sales velocity
""", agent="PostgresAgent")
```

### Data Quality Analysis

```python
# Find data issues
lui("""
Analyze the customer data for quality issues like
missing emails, duplicate records, or invalid phone numbers
""", agent="PostgresAgent")

# Referential integrity
lui("""
Find orders that reference non-existent customers
or products
""", agent="PostgresAgent")

# Data profiling
lui("""
Profile the transactions table showing distributions,
null counts, and potential anomalies
""", agent="PostgresAgent")
```

### Performance Analysis

```python
# Query performance insights
lui("""
Which queries are running slowly and could benefit
from indexes?
""", agent="PostgresAgent")

# Table statistics
lui("""
Show me the largest tables and their growth rate
over the last month
""", agent="PostgresAgent")

# Index recommendations
lui("""
Suggest indexes that would improve performance for
our most common query patterns
""", agent="PostgresAgent")
```

## PostgresPassthroughAgent (Direct SQL)

For direct SQL execution with full control:

### Basic Queries

```python
# Direct SQL execution
lui("""
SELECT c.customer_id, c.name, COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.created_at >= '2024-01-01'
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) > 5
ORDER BY order_count DESC
""", agent="PostgresPassthroughAgent")

# Access results
high_value_customers = lui.df
print(f"Found {len(high_value_customers)} high-value customers")
```

### Advanced Analytics

```python
# Window functions
lui("""
WITH sales_ranked AS (
    SELECT 
        product_id,
        sale_date,
        amount,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY amount DESC) as rank,
        SUM(amount) OVER (PARTITION BY product_id ORDER BY sale_date 
                          ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7day_sales
    FROM sales
    WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT * FROM sales_ranked WHERE rank <= 10
""", agent="PostgresPassthroughAgent")

# Recursive CTEs
lui("""
WITH RECURSIVE org_hierarchy AS (
    SELECT employee_id, name, manager_id, 0 as level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    SELECT e.employee_id, e.name, e.manager_id, oh.level + 1
    FROM employees e
    INNER JOIN org_hierarchy oh ON e.manager_id = oh.employee_id
)
SELECT * FROM org_hierarchy ORDER BY level, name
""", agent="PostgresPassthroughAgent")
```

### JSON Operations

```python
# JSONB queries
lui("""
SELECT 
    id,
    data->>'name' as name,
    data->'address'->>'city' as city,
    jsonb_array_elements(data->'orders') as order_data
FROM customers_json
WHERE data->>'status' = 'active'
AND data->'address'->>'country' = 'USA'
""", agent="PostgresPassthroughAgent")

# JSON aggregation
lui("""
SELECT 
    jsonb_build_object(
        'customer_id', customer_id,
        'total_orders', COUNT(*),
        'order_ids', jsonb_agg(order_id)
    ) as customer_summary
FROM orders
GROUP BY customer_id
""", agent="PostgresPassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use PostgresAgent when:**
- You want to describe needs in business terms
- You're exploring data relationships
- You need help with complex joins
- You want query optimization suggestions

**Use PostgresPassthroughAgent when:**
- You have exact SQL to execute
- You're running DDL operations
- You need specific PostgreSQL features
- You want full control over execution plans

### Transaction Management

```python
# AI agent handles transactions intelligently
lui("""
Update inventory levels after this order and ensure
we don't go negative
""", agent="PostgresAgent")

# Direct transaction control
lui("""
BEGIN;
UPDATE inventory SET quantity = quantity - 10 WHERE product_id = 123;
INSERT INTO inventory_log (product_id, change, timestamp) VALUES (123, -10, NOW());
COMMIT;
""", agent="PostgresPassthroughAgent")
```

### Error Handling

```python
# AI provides helpful context
lui("Show me data from the usr table", agent="PostgresAgent")
# Response: "I couldn't find a 'usr' table. Did you mean 'users'? Here are the available tables..."

# Direct execution shows raw errors
lui("SELECT * FROM usr", agent="PostgresPassthroughAgent")
# Response: ERROR: relation "usr" does not exist
```

## Common Patterns

### User Analytics

```python
# AI-assisted user segmentation
lui("""
Segment users based on their behavior patterns,
purchase history, and engagement levels
""", agent="PostgresAgent")

# Direct cohort analysis
lui("""
SELECT 
    DATE_TRUNC('month', created_at) as cohort_month,
    COUNT(DISTINCT user_id) as cohort_size,
    COUNT(DISTINCT CASE WHEN last_active > created_at + INTERVAL '30 days' 
                        THEN user_id END) as retained_30d,
    COUNT(DISTINCT CASE WHEN last_active > created_at + INTERVAL '90 days' 
                        THEN user_id END) as retained_90d
FROM users
WHERE created_at >= '2024-01-01'
GROUP BY cohort_month
ORDER BY cohort_month
""", agent="PostgresPassthroughAgent")
```

### Financial Reporting

```python
# AI handles complex financial logic
lui("""
Generate a P&L statement for last quarter with
proper account categorization and subtotals
""", agent="PostgresAgent")

# Direct financial query
lui("""
WITH categorized_transactions AS (
    SELECT 
        t.*,
        a.account_type,
        a.account_category
    FROM transactions t
    JOIN accounts a ON t.account_id = a.account_id
    WHERE t.transaction_date BETWEEN '2024-01-01' AND '2024-03-31'
)
SELECT 
    account_category,
    account_type,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as credits,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as debits,
    SUM(amount) as net
FROM categorized_transactions
GROUP BY ROLLUP(account_category, account_type)
ORDER BY account_category, account_type
""", agent="PostgresPassthroughAgent")
```

### Data Migration

```python
# AI helps with migration logic
lui("""
Create a query to migrate customer data from the old schema
to the new one, handling data transformations
""", agent="PostgresAgent")

# Direct migration SQL
lui("""
INSERT INTO customers_new (id, email, full_name, phone, created_at, metadata)
SELECT 
    customer_id,
    LOWER(email),
    CONCAT(first_name, ' ', last_name),
    REGEXP_REPLACE(phone, '[^0-9]', '', 'g'),
    created_date,
    jsonb_build_object(
        'source', 'legacy_system',
        'migrated_at', NOW(),
        'original_id', customer_id
    )
FROM customers_old
WHERE email IS NOT NULL
ON CONFLICT (email) DO UPDATE
SET metadata = customers_new.metadata || EXCLUDED.metadata
""", agent="PostgresPassthroughAgent")
```

## Integration with Other Agents

```python
# Query data with PostgreSQL
lui("Get customer purchase patterns", agent="PostgresAgent")
patterns_df = lui.df

# Visualize with Graph agent
lui("Create a graph showing customer product preferences", agent="GraphAgent")

# Generate analysis code
lui("Write Python code to predict next purchase date", agent="CodeAgent")

# Create a report
lui("Generate a markdown report of these findings", agent="TextAgent")
```

## Performance Optimization

### Index Management

```python
# AI suggests indexes
lui("""
Analyze our query patterns and suggest which indexes
would provide the most performance benefit
""", agent="PostgresAgent")

# Create specific indexes
lui("""
CREATE INDEX CONCURRENTLY idx_orders_customer_date 
ON orders(customer_id, order_date DESC) 
WHERE status = 'completed';

ANALYZE orders;
""", agent="PostgresPassthroughAgent")
```

### Query Optimization

```python
# AI optimizes automatically
lui("""
Find the top customers by revenue but make it fast,
we have millions of records
""", agent="PostgresAgent")

# Manual optimization
lui("""
EXPLAIN (ANALYZE, BUFFERS) 
SELECT c.customer_id, c.name, SUM(o.total) as revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.created_at >= '2024-01-01'
GROUP BY c.customer_id, c.name
ORDER BY revenue DESC
LIMIT 100
""", agent="PostgresPassthroughAgent")
```

## Next Steps

- Learn about other database agents in the [Agents Reference](../../reference/agents.md#database-query-agents)
- Explore [Code Agent](code.md) for data processing scripts
- See [Graph Agent](graph.md) for data visualization
- Check the [Query Patterns Guide](../query-patterns.md) for more examples