# Roleplay: DevOps Engineer Using Louie.ai Python Client

**Persona**: Alex, DevOps Engineer at a SaaS company
**Goal**: Automate system monitoring and incident investigation
**Context**: V1 minimal Python client integrated into monitoring scripts

---

**Alex**: I want to integrate Louie into our monitoring automation. First, let me set up a reusable client.

**Louie Docs**: Create a reusable client configuration:
```python
# monitoring_config.py
import os
import graphistry
from louieai import LouieClient

def get_louie_client():
    """Initialize Louie client with service account credentials"""
    graphistry.register(
        api=3, 
        username=os.getenv("LOUIE_SERVICE_ACCOUNT"),
        password=os.getenv("LOUIE_SERVICE_PASSWORD")
    )
    return LouieClient()
```

**Alex**: I need to create an automated script that checks system health every hour.

**Louie Docs**: Here's a pattern for automated monitoring:
```python
# hourly_health_check.py
from datetime import datetime
from monitoring_config import get_louie_client

def run_health_check():
    client = get_louie_client()
    
    # Create thread with timestamp
    thread = client.create_thread(
        name=f"System Health Check - {datetime.now().isoformat()}"
    )
    
    # Query multiple monitoring data sources
    response = client.add_cell(
        thread_id=thread.id,
        content="""
        Check system health across all data sources:
        1. Query OpenSearch for application logs with severity >= WARNING in last hour
        2. Query Prometheus/ClickHouse for CPU, memory, disk usage above 80%
        3. Query PostgreSQL for database connection pool stats
        Return anomalies only
        """
    )
    
    return thread.id, response
```

**Alex**: How do I handle the response programmatically to trigger alerts?

**Louie Docs**: Parse responses and integrate with your alerting system:
```python
def process_health_check(thread_id, response):
    if response.status == "error":
        # Critical: Louie itself has issues
        send_page("Louie health check failed", severity="critical")
        return
    
    # Check if any issues were found
    issues_df = response.to_dataframe()
    
    if issues_df is not None and len(issues_df) > 0:
        # Categorize issues
        critical_issues = issues_df[issues_df['severity'] == 'critical']
        warning_issues = issues_df[issues_df['severity'] == 'warning']
        
        if len(critical_issues) > 0:
            send_page(f"Critical issues detected: {critical_issues.to_dict('records')}")
        elif len(warning_issues) > 5:
            send_slack_alert(f"Multiple warnings detected. Thread: {thread_id}")
```

**Alex**: What about investigating specific incidents automatically?

**Louie Docs**: Create specialized investigation functions:
```python
def investigate_high_cpu(server_name, threshold_exceeded):
    client = get_louie_client()
    
    investigation = client.create_thread(
        name=f"High CPU Investigation - {server_name}"
    )
    
    # Multi-step investigation
    response1 = client.add_cell(
        thread_id=investigation.id,
        content=f"""
        Server {server_name} exceeded {threshold_exceeded}% CPU. Investigate:
        1. Query OpenSearch for processes consuming most CPU on {server_name}
        2. Check for any deployment events in the last 2 hours
        3. Look for correlated errors in application logs
        """
    )
    
    # Get initial findings
    findings_df = response1.to_dataframe()
    
    # Deeper dive based on findings
    if findings_df is not None:
        top_process = findings_df.iloc[0]['process_name']
        response2 = client.add_cell(
            thread_id=investigation.id,
            content=f"Analyze why {top_process} is consuming high CPU. Check for recent code changes or configuration updates."
        )
    
    return investigation.id
```

**Alex**: I need to integrate this with our on-call rotation. How do I format findings for our team?

**Louie Docs**: Create formatted reports for your team:
```python
def create_incident_report(thread_id):
    client = get_louie_client()
    
    # Get full investigation history
    history = client.get_thread_history(thread_id)
    
    # Ask Louie to summarize for on-call
    summary_response = client.add_cell(
        thread_id=thread_id,
        content="""
        Create an incident report with:
        1. Executive summary (2-3 sentences)
        2. Root cause (if identified)
        3. Affected systems
        4. Recommended immediate actions
        5. Follow-up tasks
        Format as markdown for our wiki
        """
    )
    
    return summary_response.content
```

**Alex**: Can I use this for capacity planning queries?

**Louie Docs**: Yes, use Louie for analytical queries:
```python
def capacity_planning_report():
    client = get_louie_client()
    
    thread = client.create_thread(
        name=f"Monthly Capacity Planning - {datetime.now().strftime('%Y-%m')}"
    )
    
    response = client.add_cell(
        thread_id=thread.id,
        content="""
        Analyze resource usage trends over the past 30 days:
        1. Query ClickHouse for CPU, memory, disk usage trends by service
        2. Calculate growth rate and project next 3 months
        3. Identify services approaching capacity limits
        4. Compare with last month's projections
        """
    )
    
    trends_df = response.to_dataframe()
    trends_df.to_csv(f"capacity_trends_{datetime.now().strftime('%Y%m')}.csv")
    
    return thread.id
```

**Alex**: What about error handling for production scripts?

**Louie Docs**: Implement robust error handling:
```python
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def safe_louie_query(client, thread_id, query):
    """Production-safe query with retries"""
    try:
        response = client.add_cell(thread_id=thread_id, content=query)
        if response.status == "error":
            logger.error(f"Louie query failed: {response.error_message}")
            raise RuntimeError(response.error_message)
        return response
    except Exception as e:
        logger.error(f"Failed to execute Louie query: {e}")
        raise

# Use in production
try:
    response = safe_louie_query(client, thread.id, "Check system status")
except Exception as e:
    # Fallback to direct database queries or cached results
    logger.warning("Falling back to direct queries")
```

**Alex**: How do I clean up old threads to avoid cluttering?

**Louie Docs**: Thread management for automation:
```python
def cleanup_old_threads(days_to_keep=7):
    """Archive or delete old monitoring threads"""
    client = get_louie_client()
    
    # This is hypothetical - actual API may differ
    old_threads = client.list_threads(
        created_before=datetime.now() - timedelta(days=days_to_keep)
    )
    
    for thread in old_threads:
        if "health check" in thread.name.lower():
            # Archive health checks
            history = client.get_thread_history(thread.id)
            save_to_s3(f"archives/{thread.id}.json", history)
            # client.delete_thread(thread.id)  # If API supports
```

---

## Key Documentation Needs Identified

1. **Service Account Auth**: Best practices for automation credentials
2. **Programmatic Response Handling**: Parsing structured data from responses
3. **Error Handling**: Retries, fallbacks, production safety
4. **Thread Lifecycle**: Creating, querying, archiving threads
5. **Integration Patterns**: Webhooks, alerts, monitoring systems
6. **Batch Operations**: Running multiple queries efficiently
7. **Caching/Persistence**: Storing results for compliance/history
8. **Performance**: Rate limits, timeouts, concurrent queries