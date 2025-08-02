# Spanner Agent Guide

Access Google Cloud Spanner globally distributed databases.

## Overview

- **SpannerAgent** - AI-powered natural language to Spanner SQL
- **SpannerPassthroughAgent** - Direct SQL execution

## Usage Examples

```python
# AI-assisted global queries
lui("Show user activity across all regions", agent="SpannerAgent")

# Direct SQL with Spanner features
lui("SELECT * FROM Users TABLESAMPLE RESERVOIR (1000 ROWS) AT TIMESTAMP TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 15 SECOND)", 
    agent="SpannerPassthroughAgent")
```

## Common Patterns

- Global consistency checks
- Multi-region analytics
- Performance monitoring
- Transaction analysis

## Integration

Query global data, then visualize worldwide patterns with KeplerAgent.