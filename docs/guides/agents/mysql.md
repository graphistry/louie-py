# MySQL Agent Guide

The MySQL agents provide comprehensive support for MySQL and MariaDB databases with semantic understanding of your schema and query optimization.

## Overview

- **MySQLAgent** - AI-powered natural language to SQL with MySQL-specific optimizations
- **MySQLPassthroughAgent** - Direct SQL execution without AI interpretation

## MySQLAgent (AI-Assisted)

The MySQLAgent understands:
- MySQL-specific syntax and features
- Storage engines (InnoDB, MyISAM)
- Index strategies and query optimization
- Your schema relationships and business logic

### Basic Usage

```python
from louieai.notebook import lui

# Simple queries with business context
lui("Show me our top customers by revenue", agent="MySQLAgent")

# Database exploration
lui("What tables contain user activity data?", agent="MySQLAgent")

# Performance insights
lui("Which queries are causing table locks?", agent="MySQLAgent")
```

### E-commerce Analytics

```python
# Customer behavior analysis
lui("""
Analyze customer purchase patterns including:
- Average order value by customer segment
- Repeat purchase rate
- Time between purchases
""", agent="MySQLAgent")

# Inventory management
lui("""
Find products that are low in stock considering
current sales velocity and lead time
""", agent="MySQLAgent")

# Revenue analysis
lui("""
Calculate month-over-month revenue growth
broken down by product category and region
""", agent="MySQLAgent")
```

### Performance Optimization

```python
# Index recommendations
lui("""
Analyze our slow queries and suggest indexes
that would improve performance
""", agent="MySQLAgent")

# Query optimization
lui("""
Show me expensive queries that could benefit
from query restructuring or denormalization
""", agent="MySQLAgent")

# Storage analysis
lui("""
Which tables are consuming the most disk space
and would benefit from partitioning?
""", agent="MySQLAgent")
```

### Data Quality & Validation

```python
# Referential integrity checks
lui("""
Find orphaned records across our database
where foreign keys reference non-existent records
""", agent="MySQLAgent")

# Duplicate detection
lui("""
Identify potential duplicate customer records
based on email, phone, or address similarity
""", agent="MySQLAgent")

# Data profiling
lui("""
Profile the orders table showing data distributions,
patterns, and potential anomalies
""", agent="MySQLAgent")
```

## MySQLPassthroughAgent (Direct SQL)

For direct MySQL SQL execution with full control:

### Basic Queries

```python
# Direct SQL execution
lui("""
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.quantity * oi.unit_price) as lifetime_value,
    MAX(o.order_date) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE c.created_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
GROUP BY c.customer_id, c.customer_name
HAVING lifetime_value > 1000
ORDER BY lifetime_value DESC
LIMIT 100
""", agent="MySQLPassthroughAgent")
```

### Advanced Analytics

```python
# Window functions (MySQL 8.0+)
lui("""
WITH sales_ranked AS (
    SELECT 
        product_id,
        sale_date,
        quantity,
        price,
        SUM(quantity * price) OVER (
            PARTITION BY product_id 
            ORDER BY sale_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as rolling_7day_revenue,
        RANK() OVER (
            PARTITION BY DATE(sale_date) 
            ORDER BY quantity * price DESC
        ) as daily_rank
    FROM sales
    WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
)
SELECT * FROM sales_ranked WHERE daily_rank <= 10
""", agent="MySQLPassthroughAgent")

# Common Table Expressions
lui("""
WITH RECURSIVE category_tree AS (
    SELECT 
        category_id,
        category_name,
        parent_category_id,
        0 as level,
        category_name as path
    FROM categories
    WHERE parent_category_id IS NULL
    
    UNION ALL
    
    SELECT 
        c.category_id,
        c.category_name,
        c.parent_category_id,
        ct.level + 1,
        CONCAT(ct.path, ' > ', c.category_name)
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_category_id = ct.category_id
)
SELECT * FROM category_tree ORDER BY path
""", agent="MySQLPassthroughAgent")
```

### JSON Operations (MySQL 5.7+)

```python
# JSON data handling
lui("""
SELECT 
    order_id,
    JSON_EXTRACT(metadata, '$.source') as order_source,
    JSON_EXTRACT(metadata, '$.items[*].sku') as skus,
    JSON_LENGTH(metadata, '$.items') as item_count,
    JSON_EXTRACT(customer_data, '$.preferences.notifications') as notify_prefs
FROM orders
WHERE JSON_CONTAINS(metadata, '"mobile"', '$.source')
AND created_date >= CURDATE()
""", agent="MySQLPassthroughAgent")

# JSON aggregation
lui("""
SELECT 
    product_category,
    JSON_ARRAYAGG(
        JSON_OBJECT(
            'product_id', product_id,
            'name', product_name,
            'price', price
        )
    ) as products
FROM products
WHERE active = 1
GROUP BY product_category
""", agent="MySQLPassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use MySQLAgent when:**
- You want to describe queries in business terms
- You need help with MySQL-specific syntax
- You want automatic query optimization
- You're exploring schema relationships

**Use MySQLPassthroughAgent when:**
- You have exact SQL to execute
- You need stored procedures or functions
- You want full control over query execution
- You're using MySQL-specific features

### Transaction Management

```python
# AI handles transaction logic
lui("""
Transfer inventory from warehouse A to warehouse B
ensuring stock levels don't go negative
""", agent="MySQLAgent")

# Direct transaction control
lui("""
START TRANSACTION;

UPDATE inventory 
SET quantity = quantity - 100 
WHERE warehouse_id = 'A' AND product_id = 'P123';

UPDATE inventory 
SET quantity = quantity + 100 
WHERE warehouse_id = 'B' AND product_id = 'P123';

INSERT INTO inventory_transfers (product_id, from_warehouse, to_warehouse, quantity, transfer_date)
VALUES ('P123', 'A', 'B', 100, NOW());

COMMIT;
""", agent="MySQLPassthroughAgent")
```

### Performance Tuning

```python
# AI suggests optimizations
lui("""
Optimize the customer search query that's running slowly
""", agent="MySQLAgent")

# Direct performance analysis
lui("""
EXPLAIN ANALYZE
SELECT c.*, COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.email LIKE '%@example.com'
GROUP BY c.customer_id
""", agent="MySQLPassthroughAgent")
```

## Common Patterns

### Full-Text Search

```python
# AI-powered search
lui("""
Search for products matching 'wireless headphones'
ranked by relevance
""", agent="MySQLAgent")

# Direct full-text search
lui("""
SELECT 
    product_id,
    product_name,
    description,
    MATCH(product_name, description) AGAINST('wireless headphones' IN NATURAL LANGUAGE MODE) as relevance
FROM products
WHERE MATCH(product_name, description) AGAINST('wireless headphones' IN NATURAL LANGUAGE MODE)
ORDER BY relevance DESC
LIMIT 20
""", agent="MySQLPassthroughAgent")
```

### Partitioning Strategies

```python
# AI recommends partitioning
lui("""
Suggest partitioning strategies for our large
transaction table to improve query performance
""", agent="MySQLAgent")

# Direct partition creation
lui("""
ALTER TABLE transactions 
PARTITION BY RANGE (YEAR(transaction_date)) (
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p_future VALUES LESS THAN MAXVALUE
)
""", agent="MySQLPassthroughAgent")
```

### Replication Monitoring

```python
# AI checks replication health
lui("""
Check replication status and identify any lag
or errors in our MySQL replicas
""", agent="MySQLAgent")

# Direct replication commands
lui("""
SHOW SLAVE STATUS\G
""", agent="MySQLPassthroughAgent")
```

## Integration with Other Agents

```python
# Query data with MySQL
lui("Get customer engagement metrics", agent="MySQLAgent")
metrics_df = lui.df

# Visualize with Graph agent
lui("Create a customer segmentation network", agent="GraphAgent")

# Generate analysis code
lui("Write Python code to predict customer churn from these metrics", agent="CodeAgent")

# Create monitoring
lui("Generate Splunk queries to monitor database performance", agent="SplunkAgent")
```

## MySQL-Specific Features

### Stored Procedures

```python
# AI helps create procedures
lui("""
Create a stored procedure to calculate customer
lifetime value with parameters for date range
""", agent="MySQLAgent")

# Direct procedure creation
lui("""
DELIMITER //
CREATE PROCEDURE CalculateCustomerLTV(
    IN start_date DATE,
    IN end_date DATE,
    OUT avg_ltv DECIMAL(10,2)
)
BEGIN
    SELECT AVG(customer_ltv) INTO avg_ltv
    FROM (
        SELECT 
            customer_id,
            SUM(order_total) as customer_ltv
        FROM orders
        WHERE order_date BETWEEN start_date AND end_date
        GROUP BY customer_id
    ) as ltv_calc;
END//
DELIMITER ;
""", agent="MySQLPassthroughAgent")
```

### Event Scheduling

```python
# AI creates scheduled tasks
lui("""
Create a scheduled job to archive old orders
to a history table every night at 2 AM
""", agent="MySQLAgent")

# Direct event creation
lui("""
CREATE EVENT archive_old_orders
ON SCHEDULE EVERY 1 DAY
STARTS '2024-01-01 02:00:00'
DO
BEGIN
    INSERT INTO orders_archive
    SELECT * FROM orders
    WHERE order_date < DATE_SUB(NOW(), INTERVAL 90 DAY);
    
    DELETE FROM orders
    WHERE order_date < DATE_SUB(NOW(), INTERVAL 90 DAY);
END
""", agent="MySQLPassthroughAgent")
```

## Next Steps

- Learn about [PostgreSQL Agent](postgresql.md) for PostgreSQL databases
- Explore [Snowflake Agent](snowflake.md) for cloud data warehouses
- See [BigQuery Agent](bigquery.md) for Google Cloud analytics
- Check the [Query Patterns Guide](../query-patterns.md) for more examples