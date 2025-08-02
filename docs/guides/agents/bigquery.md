# BigQuery Agent Guide

The BigQuery agents provide seamless integration with Google Cloud's serverless data warehouse, offering petabyte-scale analytics with built-in ML capabilities.

## Overview

- **BigQueryAgent** - AI-powered natural language to SQL with BigQuery-specific optimizations
- **BigQueryPassthroughAgent** - Direct SQL execution without AI interpretation

## BigQueryAgent (AI-Assisted)

The BigQueryAgent understands:
- BigQuery's architecture (datasets, tables, views)
- Cost optimization through partitioning and clustering
- Built-in ML functions and geospatial features
- Cross-dataset and cross-project queries

### Basic Usage

```python
from louieai.notebook import lui

# Simple analytics queries
lui("Show me user engagement metrics for last week", agent="BigQueryAgent")

# Dataset exploration
lui("What customer data is available across our datasets?", agent="BigQueryAgent")

# Cost estimation
lui("Estimate the cost of analyzing all historical data", agent="BigQueryAgent")
```

### Advanced Analytics

```python
# Customer segmentation
lui("""
Segment customers based on their purchase behavior,
lifetime value, and engagement patterns
""", agent="BigQueryAgent")

# Predictive analytics with BQML
lui("""
Build a model to predict customer churn using
BigQuery ML with our transaction history
""", agent="BigQueryAgent")

# Geospatial analysis
lui("""
Analyze delivery patterns and find optimal
warehouse locations based on customer density
""", agent="BigQueryAgent")
```

### Real-time Analytics

```python
# Streaming data analysis
lui("""
Analyze real-time user events from our streaming
pipeline to detect anomalies and trends
""", agent="BigQueryAgent")

# Session analysis
lui("""
Reconstruct user sessions from event streams
and calculate engagement metrics
""", agent="BigQueryAgent")

# Funnel analysis
lui("""
Build conversion funnels from raw event data
showing drop-off rates at each step
""", agent="BigQueryAgent")
```

### Cost Optimization

```python
# Query optimization
lui("""
Optimize our most expensive queries using
partitioning, clustering, and materialized views
""", agent="BigQueryAgent")

# Storage optimization
lui("""
Identify tables that would benefit from
partitioning to reduce query costs
""", agent="BigQueryAgent")

# Slot usage analysis
lui("""
Analyze our slot usage patterns and recommend
reservation strategies
""", agent="BigQueryAgent")
```

## BigQueryPassthroughAgent (Direct SQL)

For direct BigQuery SQL execution with full control:

### Basic Queries

```python
# Standard SQL with BigQuery functions
lui("""
SELECT 
    user_id,
    DATE_TRUNC(event_timestamp, DAY) as event_day,
    COUNT(*) as event_count,
    COUNT(DISTINCT session_id) as session_count,
    APPROX_QUANTILES(event_duration_ms, 100)[OFFSET(50)] as median_duration,
    APPROX_QUANTILES(event_duration_ms, 100)[OFFSET(95)] as p95_duration
FROM `project.analytics.events`
WHERE DATE(event_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    AND event_type IN ('page_view', 'click', 'purchase')
GROUP BY user_id, event_day
""", agent="BigQueryPassthroughAgent")
```

### Advanced Window Functions

```python
# Complex analytics with arrays and structs
lui("""
WITH user_journey AS (
    SELECT 
        user_id,
        ARRAY_AGG(
            STRUCT(
                event_timestamp,
                event_type,
                page_name,
                revenue
            ) ORDER BY event_timestamp
        ) as events,
        SUM(revenue) as total_revenue
    FROM `project.analytics.events`
    WHERE DATE(event_timestamp) = CURRENT_DATE()
    GROUP BY user_id
),
journey_metrics AS (
    SELECT 
        user_id,
        total_revenue,
        ARRAY_LENGTH(events) as event_count,
        events[SAFE_OFFSET(0)].event_type as first_event,
        events[SAFE_OFFSET(ARRAY_LENGTH(events)-1)].event_type as last_event,
        TIMESTAMP_DIFF(
            events[SAFE_OFFSET(ARRAY_LENGTH(events)-1)].event_timestamp,
            events[SAFE_OFFSET(0)].event_timestamp,
            MINUTE
        ) as session_duration_minutes
    FROM user_journey
)
SELECT * FROM journey_metrics
WHERE total_revenue > 0
ORDER BY total_revenue DESC
""", agent="BigQueryPassthroughAgent")
```

### BigQuery ML

```python
# Create ML model
lui("""
CREATE OR REPLACE MODEL `project.ml_models.customer_ltv`
OPTIONS(
    model_type='linear_reg',
    input_label_cols=['lifetime_value'],
    enable_global_explain=TRUE,
    data_split_method='AUTO_SPLIT'
) AS
SELECT 
    lifetime_value,
    days_since_first_purchase,
    total_orders,
    avg_order_value,
    days_between_orders,
    product_categories_purchased,
    preferred_payment_method,
    customer_segment
FROM `project.analytics.customer_features`
WHERE lifetime_value > 0
""", agent="BigQueryPassthroughAgent")

# Make predictions
lui("""
SELECT 
    customer_id,
    predicted_lifetime_value,
    predicted_lifetime_value_lower_bound,
    predicted_lifetime_value_upper_bound
FROM ML.PREDICT(
    MODEL `project.ml_models.customer_ltv`,
    (
        SELECT * FROM `project.analytics.new_customers`
        WHERE days_since_first_purchase <= 30
    )
)
""", agent="BigQueryPassthroughAgent")
```

### Geospatial Queries

```python
# Geographic analysis
lui("""
WITH store_coverage AS (
    SELECT 
        store_id,
        store_name,
        ST_GEOGPOINT(longitude, latitude) as store_location,
        ST_BUFFER(ST_GEOGPOINT(longitude, latitude), 5000) as coverage_area
    FROM `project.locations.stores`
),
customer_assignments AS (
    SELECT 
        c.customer_id,
        c.address,
        ST_GEOGPOINT(c.longitude, c.latitude) as customer_location,
        ARRAY_AGG(
            STRUCT(
                s.store_id,
                s.store_name,
                ST_DISTANCE(
                    ST_GEOGPOINT(c.longitude, c.latitude),
                    s.store_location
                ) as distance_meters
            )
            ORDER BY ST_DISTANCE(
                ST_GEOGPOINT(c.longitude, c.latitude),
                s.store_location
            )
            LIMIT 3
        ) as nearest_stores
    FROM `project.customers.addresses` c
    CROSS JOIN store_coverage s
    WHERE ST_CONTAINS(s.coverage_area, ST_GEOGPOINT(c.longitude, c.latitude))
    GROUP BY 1, 2, 3
)
SELECT * FROM customer_assignments
""", agent="BigQueryPassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use BigQueryAgent when:**
- You want to describe analytics in business terms
- You need help with BigQuery-specific features
- You want cost-optimized query generation
- You're exploring nested or repeated fields

**Use BigQueryPassthroughAgent when:**
- You have exact SQL to execute
- You're creating ML models or UDFs
- You need specific query optimization hints
- You're working with complex geospatial queries

### Partitioning and Clustering

```python
# AI suggests optimal partitioning
lui("""
Analyze our events table and suggest the best
partitioning and clustering strategy
""", agent="BigQueryAgent")

# Direct table optimization
lui("""
CREATE OR REPLACE TABLE `project.analytics.events_optimized`
PARTITION BY DATE(event_timestamp)
CLUSTER BY user_id, event_type
AS 
SELECT * FROM `project.analytics.events`;

-- Update table settings
ALTER TABLE `project.analytics.events_optimized`
SET OPTIONS (
    partition_expiration_days=90,
    require_partition_filter=true
);
""", agent="BigQueryPassthroughAgent")
```

### Cost Control

```python
# AI provides cost analysis
lui("""
Show me the most expensive queries from yesterday
and suggest optimizations
""", agent="BigQueryAgent")

# Direct cost monitoring
lui("""
SELECT 
    user_email,
    job_id,
    query,
    total_bytes_processed,
    ROUND(total_bytes_processed / POW(1024, 4), 2) as tb_processed,
    ROUND(total_bytes_processed / POW(1024, 4) * 5, 2) as estimated_cost_usd,
    total_slot_ms,
    creation_time,
    TIMESTAMP_DIFF(end_time, start_time, SECOND) as runtime_seconds
FROM `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE DATE(creation_time) = CURRENT_DATE() - 1
    AND statement_type = 'SELECT'
    AND state = 'DONE'
ORDER BY total_bytes_processed DESC
LIMIT 20
""", agent="BigQueryPassthroughAgent")
```

## Common Patterns

### Incremental Processing

```python
# AI builds incremental pipeline
lui("""
Create an incremental processing pipeline that
only processes new data since the last run
""", agent="BigQueryAgent")

# Direct incremental query
lui("""
-- Create checkpoint table
CREATE TABLE IF NOT EXISTS `project.analytics.processing_checkpoint` (
    table_name STRING,
    last_processed_timestamp TIMESTAMP,
    records_processed INT64,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Incremental processing
DECLARE last_checkpoint TIMESTAMP;

SET last_checkpoint = (
    SELECT IFNULL(MAX(last_processed_timestamp), TIMESTAMP('2024-01-01'))
    FROM `project.analytics.processing_checkpoint`
    WHERE table_name = 'events'
);

INSERT INTO `project.analytics.events_aggregated`
SELECT 
    DATE(event_timestamp) as event_date,
    user_id,
    event_type,
    COUNT(*) as event_count,
    SUM(revenue) as total_revenue
FROM `project.analytics.events`
WHERE event_timestamp > last_checkpoint
    AND event_timestamp <= CURRENT_TIMESTAMP()
GROUP BY 1, 2, 3;

-- Update checkpoint
INSERT INTO `project.analytics.processing_checkpoint`
VALUES ('events', CURRENT_TIMESTAMP(), @@row_count, CURRENT_TIMESTAMP());
""", agent="BigQueryPassthroughAgent")
```

### Data Quality Monitoring

```python
# AI creates quality checks
lui("""
Set up data quality monitoring for our critical
tables with anomaly detection
""", agent="BigQueryAgent")

# Direct quality checks
lui("""
WITH quality_metrics AS (
    SELECT 
        CURRENT_TIMESTAMP() as check_timestamp,
        'orders' as table_name,
        COUNT(*) as row_count,
        COUNT(DISTINCT order_id) as unique_orders,
        SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customer_ids,
        SUM(CASE WHEN order_total < 0 THEN 1 ELSE 0 END) as negative_totals,
        MIN(order_date) as min_date,
        MAX(order_date) as max_date,
        AVG(order_total) as avg_order_value,
        STDDEV(order_total) as stddev_order_value
    FROM `project.sales.orders`
    WHERE DATE(order_date) = CURRENT_DATE()
),
historical_stats AS (
    SELECT 
        AVG(row_count) as avg_daily_rows,
        STDDEV(row_count) as stddev_daily_rows,
        AVG(avg_order_value) as historical_avg_order_value
    FROM `project.monitoring.daily_quality_metrics`
    WHERE table_name = 'orders'
        AND check_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
)
SELECT 
    q.*,
    h.avg_daily_rows,
    ABS(q.row_count - h.avg_daily_rows) / h.stddev_daily_rows as row_count_zscore,
    CASE 
        WHEN ABS(q.row_count - h.avg_daily_rows) / h.stddev_daily_rows > 3 THEN 'ANOMALY'
        ELSE 'NORMAL'
    END as status
FROM quality_metrics q
CROSS JOIN historical_stats h
""", agent="BigQueryPassthroughAgent")
```

### External Data Federation

```python
# AI sets up external queries
lui("""
Query data from Cloud Storage and Bigtable
without loading it into BigQuery
""", agent="BigQueryAgent")

# Direct external table
lui("""
-- Create external table for Cloud Storage
CREATE OR REPLACE EXTERNAL TABLE `project.external_data.gcs_logs`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://my-bucket/logs/2024/*.parquet']
);

-- Query federated data from Bigtable
CREATE OR REPLACE EXTERNAL TABLE `project.external_data.bigtable_events`
OPTIONS (
    format = 'CLOUD_BIGTABLE',
    uris = ['https://bigtable.googleapis.com/projects/my-project/instances/my-instance/tables/events'],
    bigtable_options = '''
    {
        "columnFamilies": [{
            "familyId": "cf1",
            "columns": [{
                "qualifierString": "user_id",
                "type": "STRING"
            }, {
                "qualifierString": "event_data", 
                "type": "JSON"
            }]
        }],
        "readRowkeyAsString": true
    }
    '''
);

-- Join external and internal data
SELECT 
    b.rowkey as event_id,
    b.user_id,
    JSON_EXTRACT_SCALAR(b.event_data, '$.event_type') as event_type,
    g.log_timestamp,
    g.response_time_ms
FROM `project.external_data.bigtable_events` b
JOIN `project.external_data.gcs_logs` g
    ON b.rowkey = g.event_id
WHERE DATE(g.log_timestamp) = CURRENT_DATE()
""", agent="BigQueryPassthroughAgent")
```

## Integration with Other Agents

```python
# Extract data with BigQuery
lui("Get training data for customer segmentation", agent="BigQueryAgent")
training_df = lui.df

# Generate ML pipeline
lui("Create Python code for advanced feature engineering", agent="CodeAgent")

# Visualize segments
lui("Create an interactive map of customer locations by segment", agent="KeplerAgent")

# Document findings
lui("Generate a report explaining the segmentation methodology", agent="TextAgent")
```

## BigQuery-Specific Features

### User-Defined Functions

```python
# AI creates UDFs
lui("""
Create a function to parse user agent strings
and extract device information
""", agent="BigQueryAgent")

# Direct UDF creation
lui("""
CREATE OR REPLACE FUNCTION `project.functions.parse_user_agent`(user_agent STRING)
RETURNS STRUCT<
    device_type STRING,
    browser STRING,
    os STRING,
    is_mobile BOOL
>
LANGUAGE js AS '''
    // Simple parser - in production use a proper library
    var device_type = "desktop";
    var is_mobile = false;
    
    if (/Mobile|Android|iPhone|iPad/i.test(user_agent)) {
        is_mobile = true;
        device_type = /iPad/i.test(user_agent) ? "tablet" : "mobile";
    }
    
    var browser = "unknown";
    if (/Chrome/i.test(user_agent)) browser = "Chrome";
    else if (/Safari/i.test(user_agent)) browser = "Safari";
    else if (/Firefox/i.test(user_agent)) browser = "Firefox";
    
    var os = "unknown";
    if (/Windows/i.test(user_agent)) os = "Windows";
    else if (/Mac OS/i.test(user_agent)) os = "MacOS";
    else if (/Android/i.test(user_agent)) os = "Android";
    else if (/iOS|iPhone|iPad/i.test(user_agent)) os = "iOS";
    
    return {
        device_type: device_type,
        browser: browser,
        os: os,
        is_mobile: is_mobile
    };
''';

-- Use the UDF
SELECT 
    user_id,
    `project.functions.parse_user_agent`(user_agent).*,
    COUNT(*) as page_views
FROM `project.analytics.web_logs`
GROUP BY 1, 2, 3, 4, 5
""", agent="BigQueryPassthroughAgent")
```

### Scheduled Queries

```python
# AI sets up scheduled analytics
lui("""
Create a scheduled query to update our customer
metrics dashboard every hour
""", agent="BigQueryAgent")

# Direct scheduled query via API
lui("""
-- This would typically be done via BigQuery UI or API
-- Example query to be scheduled:
CREATE OR REPLACE TABLE `project.reporting.hourly_metrics`
PARTITION BY DATE(metric_timestamp)
AS
SELECT 
    CURRENT_TIMESTAMP() as metric_timestamp,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(*) as total_events,
    SUM(revenue) as total_revenue,
    AVG(session_duration_seconds) as avg_session_duration,
    APPROX_TOP_COUNT(event_type, 10) as top_events
FROM `project.analytics.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
""", agent="BigQueryPassthroughAgent")
```

## Next Steps

- Learn about [Athena Agent](athena.md) for serverless queries on S3
- Explore [Snowflake Agent](snowflake.md) for cloud data warehousing  
- See [OpenSearch Agent](opensearch.md) for log analytics
- Check the [Query Patterns Guide](../query-patterns.md) for more examples