# Snowflake Agent Guide

The Snowflake agents provide enterprise-grade cloud data warehouse capabilities with advanced analytics and semantic understanding of your Snowflake environment.

## Overview

- **SnowflakeAgent** - AI-powered natural language to SQL with Snowflake-specific optimizations
- **SnowflakePassthroughAgent** - Direct SQL execution without AI interpretation

## SnowflakeAgent (AI-Assisted)

The SnowflakeAgent understands:
- Snowflake architecture (databases, schemas, warehouses)
- Time travel and data sharing features
- Semi-structured data handling (JSON, Parquet, Avro)
- Cost optimization strategies

### Basic Usage

```python
from louieai.notebook import lui

# Simple analytics queries
lui("Show me daily revenue trends for the last quarter", agent="SnowflakeAgent")

# Schema exploration
lui("What data is available about customer transactions?", agent="SnowflakeAgent")

# Cost analysis
lui("Which queries consumed the most credits yesterday?", agent="SnowflakeAgent")
```

### Advanced Analytics

```python
# Time series analysis
lui("""
Analyze seasonal patterns in sales data with
year-over-year comparisons and growth rates
""", agent="SnowflakeAgent")

# Customer 360 view
lui("""
Create a comprehensive customer profile combining
transaction data, support tickets, and web activity
""", agent="SnowflakeAgent")

# Predictive analytics
lui("""
Calculate customer churn probability based on
usage patterns and engagement metrics
""", agent="SnowflakeAgent")
```

### Semi-Structured Data Analysis

```python
# JSON data exploration
lui("""
Extract and analyze data from our JSON event logs
focusing on user behavior patterns
""", agent="SnowflakeAgent")

# Nested data flattening
lui("""
Flatten the complex product catalog JSON to analyze
pricing trends across categories and variants
""", agent="SnowflakeAgent")

# Log file analysis
lui("""
Parse and analyze application logs stored as
semi-structured data for error patterns
""", agent="SnowflakeAgent")
```

### Performance & Cost Optimization

```python
# Query optimization
lui("""
Identify expensive queries and suggest optimizations
using clustering keys and materialized views
""", agent="SnowflakeAgent")

# Warehouse sizing
lui("""
Analyze workload patterns and recommend optimal
warehouse sizes for different workloads
""", agent="SnowflakeAgent")

# Storage optimization
lui("""
Find opportunities to reduce storage costs through
better compression and data lifecycle management
""", agent="SnowflakeAgent")
```

## SnowflakePassthroughAgent (Direct SQL)

For direct Snowflake SQL execution with full control:

### Basic Queries

```python
# Direct SQL with Snowflake syntax
lui("""
SELECT 
    DATE_TRUNC('day', order_date) as order_day,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(*) as total_orders,
    SUM(order_total) as revenue,
    AVG(order_total) as avg_order_value
FROM sales.orders
WHERE order_date >= DATEADD('month', -3, CURRENT_DATE())
GROUP BY 1
ORDER BY 1 DESC
""", agent="SnowflakePassthroughAgent")
```

### Advanced Window Functions

```python
# Complex analytics with window functions
lui("""
WITH customer_metrics AS (
    SELECT 
        customer_id,
        order_date,
        order_total,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) as order_num,
        LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) as prev_order_date,
        SUM(order_total) OVER (
            PARTITION BY customer_id 
            ORDER BY order_date 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as running_total,
        AVG(order_total) OVER (
            PARTITION BY customer_id 
            ORDER BY order_date 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) as moving_avg_3_orders
    FROM orders
),
customer_summary AS (
    SELECT 
        customer_id,
        MIN(order_date) as first_order,
        MAX(order_date) as last_order,
        COUNT(*) as total_orders,
        SUM(order_total) as lifetime_value,
        AVG(DATEDIFF('day', prev_order_date, order_date)) as avg_days_between_orders
    FROM customer_metrics
    GROUP BY customer_id
)
SELECT * FROM customer_summary
WHERE lifetime_value > 1000
ORDER BY lifetime_value DESC
""", agent="SnowflakePassthroughAgent")
```

### Semi-Structured Data Operations

```python
# JSON parsing and analysis
lui("""
SELECT 
    raw_json:timestamp::timestamp as event_time,
    raw_json:user_id::string as user_id,
    raw_json:event_type::string as event_type,
    raw_json:properties:page_name::string as page_name,
    raw_json:properties:duration_ms::number as duration_ms,
    ARRAY_SIZE(raw_json:properties:items) as item_count
FROM events.raw_events
WHERE raw_json:event_type = 'page_view'
    AND event_time >= CURRENT_DATE() - 7
QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time DESC) = 1
""", agent="SnowflakePassthroughAgent")

# Flatten nested arrays
lui("""
SELECT 
    o.order_id,
    o.customer_id,
    i.value:product_id::string as product_id,
    i.value:quantity::number as quantity,
    i.value:price::number as price,
    i.value:discount::number as discount
FROM orders o,
LATERAL FLATTEN(input => o.items) i
WHERE o.order_date >= '2024-01-01'
""", agent="SnowflakePassthroughAgent")
```

### Time Travel & Data Sharing

```python
# Query historical data
lui("""
SELECT * FROM customers AT(TIMESTAMP => '2024-01-15 10:00:00'::timestamp)
WHERE customer_id = 'C12345'
""", agent="SnowflakePassthroughAgent")

# Compare data changes
lui("""
SELECT 
    current.product_id,
    current.price as current_price,
    historical.price as historical_price,
    current.price - historical.price as price_change,
    ROUND((current.price - historical.price) / historical.price * 100, 2) as pct_change
FROM products current
JOIN products AT(OFFSET => -86400) historical 
    ON current.product_id = historical.product_id
WHERE current.price != historical.price
""", agent="SnowflakePassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use SnowflakeAgent when:**
- You want to describe analytics in business terms
- You need help with Snowflake-specific features
- You want cost-optimized query generation
- You're exploring semi-structured data

**Use SnowflakePassthroughAgent when:**
- You have exact SQL to execute
- You're using advanced Snowflake features
- You need precise control over warehouse usage
- You're working with time travel or cloning

### Warehouse Management

```python
# AI optimizes warehouse usage
lui("""
Run this analysis using the most cost-effective
warehouse size based on the data volume
""", agent="SnowflakeAgent")

# Direct warehouse control
lui("""
USE WAREHOUSE ANALYTICS_XL;

-- Your complex query here
SELECT ...;

USE WAREHOUSE ANALYTICS_XS;
""", agent="SnowflakePassthroughAgent")
```

### Cost Control

```python
# AI suggests cost savings
lui("""
Analyze our Snowflake usage and suggest ways
to reduce costs without impacting performance
""", agent="SnowflakeAgent")

# Direct resource monitoring
lui("""
SELECT 
    WAREHOUSE_NAME,
    DATE_TRUNC('hour', START_TIME) as hour,
    SUM(CREDITS_USED) as credits,
    COUNT(*) as query_count,
    AVG(EXECUTION_TIME)/1000 as avg_exec_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD('day', -7, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY 3 DESC
""", agent="SnowflakePassthroughAgent")
```

## Common Patterns

### Data Pipeline Monitoring

```python
# AI monitors pipeline health
lui("""
Check the status of our daily data pipelines and
identify any failures or delays
""", agent="SnowflakeAgent")

# Direct pipeline queries
lui("""
WITH pipeline_status AS (
    SELECT 
        TASK_NAME,
        STATE,
        SCHEDULED_TIME,
        COMPLETED_TIME,
        ERROR_MESSAGE,
        DATEDIFF('minute', SCHEDULED_TIME, COMPLETED_TIME) as duration_minutes
    FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
        SCHEDULED_TIME_RANGE_START => DATEADD('hour', -24, CURRENT_TIMESTAMP()),
        RESULT_LIMIT => 1000
    ))
)
SELECT 
    TASK_NAME,
    COUNT(*) as runs,
    SUM(CASE WHEN STATE = 'SUCCEEDED' THEN 1 ELSE 0 END) as succeeded,
    SUM(CASE WHEN STATE = 'FAILED' THEN 1 ELSE 0 END) as failed,
    AVG(duration_minutes) as avg_duration,
    MAX(duration_minutes) as max_duration
FROM pipeline_status
GROUP BY TASK_NAME
""", agent="SnowflakePassthroughAgent")
```

### Dynamic Data Masking

```python
# AI implements data privacy
lui("""
Create views that mask sensitive customer data
for non-privileged users
""", agent="SnowflakeAgent")

# Direct masking implementation
lui("""
CREATE OR REPLACE MASKING POLICY email_mask AS (val string) 
RETURNS string ->
    CASE
        WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
        ELSE CONCAT(LEFT(val, 2), '****', '@', SPLIT_PART(val, '@', 2))
    END;

ALTER TABLE customers MODIFY COLUMN email SET MASKING POLICY email_mask;
""", agent="SnowflakePassthroughAgent")
```

### External Data Integration

```python
# AI helps with external tables
lui("""
Set up external tables to query data directly
from our S3 data lake
""", agent="SnowflakeAgent")

# Direct external table creation
lui("""
CREATE OR REPLACE EXTERNAL TABLE s3_events (
    event_date DATE AS TO_DATE(SUBSTR(metadata$filename, 8, 10), 'YYYY-MM-DD'),
    event_data VARIANT AS (VALUE::VARIANT)
)
WITH LOCATION = @my_s3_stage/events/
FILE_FORMAT = (TYPE = PARQUET)
AUTO_REFRESH = TRUE;

SELECT 
    event_date,
    event_data:user_id::string as user_id,
    event_data:event_type::string as event_type
FROM s3_events
WHERE event_date >= CURRENT_DATE() - 7
""", agent="SnowflakePassthroughAgent")
```

## Integration with Other Agents

```python
# Extract data with Snowflake
lui("Get customer behavior metrics for ML model", agent="SnowflakeAgent")
training_data = lui.df

# Generate feature engineering code
lui("Create Python code for feature engineering on this data", agent="CodeAgent")

# Visualize patterns
lui("Create an interactive dashboard of these metrics", agent="PerspectiveAgent")

# Monitor in production
lui("Generate queries to monitor model drift in production", agent="SnowflakeAgent")
```

## Snowflake-Specific Features

### Streams and Tasks

```python
# AI creates change data capture
lui("""
Set up a stream to capture changes in the orders table
and a task to process them every hour
""", agent="SnowflakeAgent")

# Direct stream and task creation
lui("""
-- Create stream
CREATE OR REPLACE STREAM orders_changes ON TABLE orders;

-- Create processing task
CREATE OR REPLACE TASK process_order_changes
    WAREHOUSE = ANALYTICS_XS
    SCHEDULE = 'USING CRON 0 * * * * UTC'
AS
    INSERT INTO orders_summary
    SELECT 
        CURRENT_TIMESTAMP() as process_time,
        SYSTEM$STREAM_GET_TABLE_TIMESTAMP('orders_changes') as stream_timestamp,
        COUNT(*) as change_count,
        SUM(CASE WHEN METADATA$ACTION = 'INSERT' THEN 1 ELSE 0 END) as inserts,
        SUM(CASE WHEN METADATA$ACTION = 'DELETE' THEN 1 ELSE 0 END) as deletes
    FROM orders_changes;

ALTER TASK process_order_changes RESUME;
""", agent="SnowflakePassthroughAgent")
```

### Data Sharing

```python
# AI sets up secure sharing
lui("""
Create a secure share for our partners containing
aggregated sales data without exposing customer PII
""", agent="SnowflakeAgent")

# Direct share creation
lui("""
CREATE OR REPLACE SHARE sales_analytics_share;

GRANT USAGE ON DATABASE analytics TO SHARE sales_analytics_share;
GRANT USAGE ON SCHEMA analytics.aggregated TO SHARE sales_analytics_share;
GRANT SELECT ON VIEW analytics.aggregated.daily_sales_summary TO SHARE sales_analytics_share;

ALTER SHARE sales_analytics_share ADD ACCOUNTS = partner_account_id;
""", agent="SnowflakePassthroughAgent")
```

## Next Steps

- Learn about [BigQuery Agent](bigquery.md) for Google Cloud analytics
- Explore [Databricks Agent](databricks.md) for unified analytics
- See [Athena Agent](athena.md) for serverless SQL queries
- Check the [Query Patterns Guide](../query-patterns.md) for more examples