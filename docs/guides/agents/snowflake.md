# Snowflake Agent Guide

Access Snowflake cloud data warehouse with natural language or direct SQL.

## Overview

- **SnowflakeAgent** - AI-powered natural language to SQL
- **SnowflakePassthroughAgent** - Direct SQL execution

## Usage Examples

```python
# AI-assisted analytics queries
lui("Show me daily revenue trends for the last quarter", agent="SnowflakeAgent")

# Semi-structured data analysis
lui("Extract user behavior patterns from our JSON event logs", agent="SnowflakeAgent")

# Direct SQL with Snowflake features
lui("SELECT * FROM customers AT(TIMESTAMP => '2024-01-15 10:00:00'::timestamp)", 
    agent="SnowflakePassthroughAgent")

# JSON operations
lui("SELECT raw_json:user_id::string, raw_json:event_type::string FROM events", 
    agent="SnowflakePassthroughAgent")
```

## Common Patterns

- Time series analytics
- Semi-structured data processing
- Cost optimization analysis
- Time travel queries

## Integration

Extract data with SnowflakeAgent, then create features with CodeAgent or visualize with PerspectiveAgent.