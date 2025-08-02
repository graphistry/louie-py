# Splunk Agent Guide

Access Splunk for log analysis with natural language or SPL queries.

## Overview

- **SplunkAgent** - AI-powered natural language to SPL
- **SplunkPassthroughAgent** - Direct SPL execution

## Usage Examples

```python
# AI-assisted security analysis
lui("Show me failed login attempts in the last hour", agent="SplunkAgent")

# Performance monitoring
lui("Find the slowest API endpoints today", agent="SplunkAgent")

# Direct SPL execution
lui("index=web_logs status=404 | stats count by uri | sort -count | head 20", 
    agent="SplunkPassthroughAgent")

# Event correlation
lui("index=security event_type=\"failed_login\" | timechart span=5m count by src_ip", 
    agent="SplunkPassthroughAgent")
```

## Common Patterns

- Security incident investigation
- Log pattern analysis
- Performance monitoring
- Compliance reporting

## Integration

Analyze logs with SplunkAgent, then create visualizations with GraphAgent or generate reports with CodeAgent.