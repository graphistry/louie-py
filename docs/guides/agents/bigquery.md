# BigQuery Agent Guide

Access Google Cloud BigQuery with natural language or direct SQL.

## Overview

- **BigQueryAgent** - AI-powered natural language to SQL
- **BigQueryPassthroughAgent** - Direct SQL execution

## Usage Examples

```python
# AI-assisted analytics queries
lui("Show me user engagement metrics for last week", agent="BigQueryAgent")

# Cost optimization
lui("Estimate the cost of analyzing all historical data", agent="BigQueryAgent")

# Direct SQL with BigQuery features
lui("SELECT user_id, APPROX_QUANTILES(duration_ms, 100)[OFFSET(50)] as median FROM events GROUP BY user_id", 
    agent="BigQueryPassthroughAgent")

# ML model creation
lui("CREATE MODEL `project.ml.churn_model` OPTIONS(model_type='logistic_reg') AS SELECT * FROM training_data", 
    agent="BigQueryPassthroughAgent")
```

## Common Patterns

- Petabyte-scale analytics
- Real-time streaming analysis
- Machine learning with BQML
- Geospatial analysis

## Integration

Extract data with BigQueryAgent, then create ML features with CodeAgent or visualize with KeplerAgent.