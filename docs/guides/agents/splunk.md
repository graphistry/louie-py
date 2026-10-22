# Splunk Agent Guide

Access Splunk for log analysis with natural language or SPL queries.

## Overview

- **Splunk** - AI-powered natural language to SPL
- **SplunkPassthrough** - Direct SPL execution

> **Agent names:** these agents are named `Splunk` and `SplunkPassthrough`, without the usual `Agent` suffix. Older Louie servers used `SplunkAgent` / `SplunkPassthroughAgent`; current ones reject those with `400 Invalid agent`.

## Usage Examples

```python
# AI-assisted security analysis
lui("Show me failed login attempts in the last hour", agent="Splunk")

# Performance monitoring
lui("Find the slowest API endpoints today", agent="Splunk")

# Direct SPL execution
lui("index=web_logs status=404 | stats count by uri | sort -count | head 20", 
    agent="SplunkPassthrough")

# Event correlation
lui("index=security event_type=\"failed_login\" | timechart span=5m count by src_ip", 
    agent="SplunkPassthrough")
```

## Common Patterns

- Security incident investigation
- Log pattern analysis
- Performance monitoring
- Compliance reporting

## Integration

Analyze logs with Splunk, then create visualizations with GraphAgent or generate reports with CodeAgent.