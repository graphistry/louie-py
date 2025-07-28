# Roleplay: Security Analyst Using Louie.ai Python Client

**Persona**: Sarah, Senior Security Analyst at a financial services company
**Goal**: Investigate suspicious login patterns across multiple data sources
**Context**: V1 minimal Python client focusing on core functionality

---

**Sarah**: I need to set up the Louie client to investigate some suspicious login activity. Let me start by authenticating.

**Louie Docs**: First, authenticate with your Graphistry credentials:
```python
import graphistry
from louieai import LouieClient

graphistry.register(api=3, username="sarah@finserv.com", password="***")
client = LouieClient()
```

**Sarah**: Great, I'm authenticated. Now I need to create a new investigation thread for this incident.

**Louie Docs**: Create a new conversation thread (dthread) for your investigation:
```python
thread = client.create_thread(
    name="Suspicious Login Investigation - Case #1247"
)
print(f"Started investigation thread: {thread.id}")
```

**Sarah**: Perfect. Now let me query our Splunk logs for failed login attempts in the last 24 hours.

**Louie Docs**: Add a cell to your thread with your query:
```python
response = client.add_cell(
    thread_id=thread.id,
    content="Search Splunk for failed login attempts in the last 24 hours, group by username and source IP"
)
```

**Sarah**: How do I know when the query is complete and get the results?

**Louie Docs**: The response object contains the status and results:
```python
if response.status == "completed":
    # Get results as a pandas DataFrame
    df = response.to_dataframe()
    print(f"Found {len(df)} suspicious login patterns")
    print(df.head())
elif response.status == "error":
    print(f"Query failed: {response.error_message}")
```

**Sarah**: I see some concerning patterns. Let me cross-reference with our SQL user database to check if these are valid users.

**Louie Docs**: You can add follow-up queries to the same thread:
```python
# Get the suspicious usernames from previous results
suspicious_users = df['username'].unique().tolist()

response2 = client.add_cell(
    thread_id=thread.id,
    content=f"Query our PostgreSQL user database to check if these users exist and their account status: {suspicious_users}"
)

user_data = response2.to_dataframe()
```

**Sarah**: This is revealing some compromised accounts. Can I get a summary of the findings?

**Louie Docs**: Louie can analyze and summarize your investigation:
```python
summary_response = client.add_cell(
    thread_id=thread.id,
    content="Summarize the security findings from the Splunk logs and user database queries. Identify the highest risk accounts."
)

print(summary_response.content)  # Natural language summary
```

**Sarah**: I need to save these results for my incident report. How do I export the data?

**Louie Docs**: You can export DataFrames and save the investigation thread:
```python
# Export DataFrames
df.to_csv("failed_logins_analysis.csv", index=False)
user_data.to_csv("compromised_accounts.csv", index=False)

# Get the full investigation history
history = client.get_thread_history(thread.id)
with open("investigation_case_1247.json", "w") as f:
    json.dump(history, f, indent=2)
```

**Sarah**: What if I need to continue this investigation tomorrow?

**Louie Docs**: You can resume a thread by its ID:
```python
# Tomorrow, resume the investigation
resumed_thread = client.get_thread(thread_id="thread_abc123")

# Continue adding cells
response = client.add_cell(
    thread_id=resumed_thread.id,
    content="Check if any of the suspicious IPs accessed other systems"
)
```

**Sarah**: One more thing - how do I handle errors if a data source is unavailable?

**Louie Docs**: The client provides detailed error information:
```python
try:
    response = client.add_cell(
        thread_id=thread.id,
        content="Query the backup Kusto cluster for additional logs"
    )
except RuntimeError as e:
    print(f"Query failed: {e}")
    # Log the error but continue investigation
    error_response = client.add_cell(
        thread_id=thread.id,
        content="Note: Kusto cluster unavailable, continuing with available data sources"
    )
```

---

## Key Documentation Needs Identified

1. **Authentication**: Clear setup with Graphistry integration
2. **Thread Management**: Creating and resuming investigations
3. **Query Patterns**: Examples for different data sources (Splunk, SQL)
4. **Response Handling**: Working with DataFrame results
5. **Error Handling**: Graceful handling of unavailable data sources
6. **Data Export**: Saving results and investigation history
7. **Multi-turn Conversations**: Building on previous results