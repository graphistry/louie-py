# Splunk Agent Guide

The Splunk agents provide powerful log analysis capabilities, offering both AI-assisted SPL query generation and direct SPL execution.

## Overview

- **SplunkAgent** - AI-powered natural language to SPL with log pattern understanding
- **SplunkPassthroughAgent** - Direct SPL execution without AI interpretation

## SplunkAgent (AI-Assisted)

The SplunkAgent understands:
- Common log formats and patterns
- Security event schemas
- Performance metrics
- Your specific index structure and sourcetypes

### Basic Usage

```python
from louieai.notebook import lui

# Simple security queries
lui("Show me failed login attempts in the last hour", agent="SplunkAgent")

# Performance analysis
lui("Find the slowest API endpoints today", agent="SplunkAgent")

# Error investigation
lui("What are the most common errors in the application logs?", agent="SplunkAgent")
```

### Security Analysis

```python
# Threat detection
lui("""
Find potential brute force attacks by looking for 
multiple failed logins followed by a success
""", agent="SplunkAgent")

# Anomaly detection
lui("""
Show me unusual spikes in network traffic 
compared to the same time last week
""", agent="SplunkAgent")

# User behavior analysis
lui("""
Identify users with suspicious access patterns,
like accessing systems outside normal hours
""", agent="SplunkAgent")
```

### Log Pattern Analysis

```python
# Error pattern clustering
lui("""
Group similar error messages together and show me 
the most common error patterns with examples
""", agent="SplunkAgent")

# Transaction analysis
lui("""
Track user sessions from login to logout,
calculating session duration and actions performed
""", agent="SplunkAgent")

# Multi-tier correlation
lui("""
Correlate frontend errors with backend API failures 
and database timeouts in the same time window
""", agent="SplunkAgent")
```

### Performance Monitoring

```python
# Application performance
lui("""
Calculate the 95th percentile response time 
for each API endpoint over the last 24 hours
""", agent="SplunkAgent")

# Resource utilization
lui("""
Show me servers with CPU usage over 80% 
and correlate with application response times
""", agent="SplunkAgent")

# Capacity planning
lui("""
Analyze growth trends in log volume and 
project storage needs for next quarter
""", agent="SplunkAgent")
```

## SplunkPassthroughAgent (Direct SPL)

For direct SPL execution when you need precise control:

### Basic Searches

```python
# Direct SPL search
lui("""
index=web_logs status=404 
| stats count by uri 
| sort -count 
| head 20
""", agent="SplunkPassthroughAgent")

# Time-based analysis
lui("""
index=security event_type="failed_login" earliest=-1h
| timechart span=5m count by src_ip
""", agent="SplunkPassthroughAgent")
```

### Advanced SPL

```python
# Complex event correlation
lui("""
index=security event_type="failed_login" 
| join type=inner user [
    search index=security event_type="successful_login" 
    | stats latest(_time) as success_time by user
]
| where _time < success_time AND _time > success_time - 300
| stats count by user, src_ip
""", agent="SplunkPassthroughAgent")

# Transaction tracking
lui("""
index=web_logs 
| transaction session_id startswith="login" endswith="logout" 
| eval duration=round(duration/60, 2) 
| stats avg(duration) as avg_session_min, max(duration) as max_session_min by user_type
""", agent="SplunkPassthroughAgent")
```

### Subsearches and Lookups

```python
# Using subsearches
lui("""
index=web_logs [
    search index=threat_intel 
    | fields malicious_ip 
    | rename malicious_ip as src_ip
]
| stats count by src_ip, action
""", agent="SplunkPassthroughAgent")

# Lookup enrichment
lui("""
index=firewall 
| lookup geo_ip ip as src_ip OUTPUT country, city 
| stats count by country 
| sort -count
""", agent="SplunkPassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use SplunkAgent when:**
- You want to describe security scenarios in plain language
- You're exploring logs without knowing exact field names
- You need help constructing complex correlations
- You want automated time range suggestions

**Use SplunkPassthroughAgent when:**
- You have exact SPL queries to run
- You're using advanced SPL features like macros
- You need precise control over search performance
- You're working with custom commands or lookups

### Performance Optimization

```python
# Let AI optimize the search
lui("""
Find all errors but make the search efficient,
limit to necessary fields only
""", agent="SplunkAgent")

# Direct optimization control
lui("""
index=web_logs earliest=-1h 
| fields _time, status, response_time, uri 
| search status>=400 
| stats count by status, uri 
| sort -count
""", agent="SplunkPassthroughAgent")
```

### Time Range Best Practices

```python
# AI agent suggests appropriate time ranges
lui("Show me login failures (pick appropriate time range)", agent="SplunkAgent")

# Explicit time control
lui("""
index=security earliest=-7d@d latest=@d
| timechart span=1d count by event_type
""", agent="SplunkPassthroughAgent")
```

## Common Security Use Cases

### Incident Investigation

```python
# AI-assisted investigation
lui("""
Investigate all activity from IP 192.168.1.100 including
web logs, firewall, and authentication events
""", agent="SplunkAgent")

# Direct correlation query
lui("""
index=* src_ip="192.168.1.100" OR dest_ip="192.168.1.100"
| eval event_source=case(
    index="web_logs", "Web",
    index="firewall", "Firewall", 
    index="auth", "Authentication",
    1=1, "Other"
)
| sort _time
| table _time event_source action user status
""", agent="SplunkPassthroughAgent")
```

### Compliance Monitoring

```python
# AI-generated compliance checks
lui("""
Check for any unauthorized access to sensitive data
as defined in our compliance policies
""", agent="SplunkAgent")

# Direct compliance query
lui("""
index=audit action="file_access" 
| lookup sensitive_data_list.csv filename OUTPUT classification
| where classification="PII" OR classification="PCI"
| stats count by user, classification, action
""", agent="SplunkPassthroughAgent")
```

## Integration with Other Agents

```python
# Analyze with Splunk
lui("Find all security incidents in the last 24 hours", agent="SplunkAgent")
incident_df = lui.df

# Visualize with Graph agent
lui("Create a network graph of attacker IPs and targeted systems", agent="GraphAgent")

# Generate report with Code agent
lui("Create a Python script to generate a security incident report", agent="CodeAgent")

# Store in database
lui("Generate SQL to store these incidents in our tracking database", agent="PostgresAgent")
```

## Advanced Features

### Alert Creation

```python
# AI helps create alert logic
lui("""
Create a search that would detect potential data exfiltration
based on unusual outbound traffic patterns
""", agent="SplunkAgent")

# Direct alert search
lui("""
index=network dest_port=443 
| bin _time span=1h 
| stats sum(bytes_out) as total_bytes by src_ip, _time 
| eventstats avg(total_bytes) as avg_bytes, stdev(total_bytes) as stdev_bytes by src_ip 
| where total_bytes > avg_bytes + (2 * stdev_bytes)
""", agent="SplunkPassthroughAgent")
```

### Dashboard Creation

```python
# AI suggests dashboard panels
lui("""
What searches would make a good security operations dashboard?
""", agent="SplunkAgent")

# Execute specific panel search
lui("""
index=security 
| stats count by event_type 
| eval severity=case(
    event_type IN ("failed_login", "invalid_user"), "Low",
    event_type IN ("privilege_escalation", "policy_violation"), "Medium",
    event_type IN ("malware_detected", "data_breach"), "High",
    1=1, "Info"
)
""", agent="SplunkPassthroughAgent")
```

## Next Steps

- Learn about [PostgreSQL Agent](postgresql.md) for database queries
- Explore [Graph Agent](graph.md) for network visualizations
- See [Code Agent](code.md) for Python automation
- Check the [Query Patterns Guide](../query-patterns.md) for more examples