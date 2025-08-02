# Kusto Agent Guide

Access Azure Data Explorer using KQL (Kusto Query Language).

## Overview

- **KustoAgent** - AI-powered natural language to KQL
- **KustoPassthroughAgent** - Direct KQL execution

## Usage Examples

```python
# AI-assisted log analysis
lui("Show error counts by hour", agent="KustoAgent")

# Direct KQL
lui("requests | where timestamp > ago(1h) | summarize count() by bin(timestamp, 5m)", 
    agent="KustoPassthroughAgent")
```

## Common Patterns

- Log analysis and monitoring
- Performance metrics
- Anomaly detection
- Time series analysis

## Integration

Query telemetry data, then visualize trends with PerspectiveAgent.