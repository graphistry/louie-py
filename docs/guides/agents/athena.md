# Athena Agent Guide

Serverless SQL queries on data stored in Amazon S3.

## Overview

- **AthenaAgent** - AI-powered natural language to Athena SQL
- **AthenaPassthroughAgent** - Direct SQL execution

## Usage Examples

```python
# AI-assisted data lake queries
lui("Show events from yesterday's log files", agent="AthenaAgent")

# Direct SQL for S3 data
lui("SELECT * FROM logs WHERE year='2024' AND month='01' AND day='15'", 
    agent="AthenaPassthroughAgent")
```

## Common Patterns

- Log analysis
- Data lake exploration
- Cost optimization
- Cross-format queries

## Integration

Query S3 data, then process with CodeAgent or visualize with PerspectiveAgent.