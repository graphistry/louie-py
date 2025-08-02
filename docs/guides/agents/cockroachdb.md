# CockroachDB Agent Guide

Access CockroachDB distributed SQL databases.

## Overview

- **CockroachDBAgent** - AI-powered natural language to distributed SQL
- **CockroachDBPassthroughAgent** - Direct SQL execution

## Usage Examples

```python
# AI-assisted distributed queries
lui("Show user activity across all regions", agent="CockroachDBAgent")

# Direct SQL with CockroachDB features
lui("SELECT region, COUNT(*) FROM users AS OF SYSTEM TIME follower_read_timestamp() GROUP BY region", 
    agent="CockroachDBPassthroughAgent")
```

## Common Patterns

- Multi-region queries
- Global data analysis
- Performance monitoring
- Distributed transactions

## Integration

Query distributed data, then visualize with KeplerAgent for geographic insights.