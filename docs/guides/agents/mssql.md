# MSSQL Agent Guide

Access Microsoft SQL Server databases with T-SQL.

## Overview

- **MSSQLAgent** - AI-powered natural language to T-SQL
- **MSSQLPassthroughAgent** - Direct T-SQL execution

## Usage Examples

```python
# AI-assisted business queries
lui("Show total sales by region this quarter", agent="MSSQLAgent")

# Direct T-SQL
lui("SELECT Region, SUM(Amount) FROM Sales WHERE Quarter = 1 GROUP BY Region", 
    agent="MSSQLPassthroughAgent")
```

## Common Patterns

- Business reporting
- Data validation
- Performance monitoring
- Financial analysis

## Integration

Query business data, then create dashboards with PerspectiveAgent.