# OpenSearch Agent Guide

Access OpenSearch for log analysis and search with natural language or query DSL.

## Overview

- **OpenSearchAgent** - AI-powered natural language to OpenSearch DSL
- **OpenSearchPassthroughAgent** - Direct query DSL execution

## Usage Examples

```python
# AI-assisted log analysis  
lui("Show me all error logs from the API service today", agent="OpenSearchAgent")

# Security monitoring
lui("Find failed authentication attempts in the last hour", agent="OpenSearchAgent")

# Direct query DSL
lui('{"query": {"match": {"level": "ERROR"}}, "aggs": {"errors_over_time": {"date_histogram": {"field": "@timestamp", "fixed_interval": "5m"}}}}', 
    agent="OpenSearchPassthroughAgent")

# Performance monitoring
lui("What are the slowest API endpoints this week?", agent="OpenSearchAgent")
```

## Common Patterns

- Log analysis and monitoring
- Security event investigation  
- Performance analytics
- Anomaly detection

## Integration

Search logs with OpenSearchAgent, then analyze patterns with CodeAgent or visualize with PerspectiveAgent.