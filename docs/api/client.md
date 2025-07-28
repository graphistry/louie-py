# LouieClient

The main client class for interacting with the Louie.ai service.

## API Documentation

::: louieai.LouieClient

## Usage Examples

### Thread-Based Conversations

```python
import louieai
import graphistry

# First authenticate with Graphistry
graphistry.register(api=3, username="your_user", password="your_pass")

# Create client
client = louieai.LouieClient()

# Start a new thread with a query
thread = client.create_thread(
    name="Network Analysis",
    initial_prompt="Analyze the network patterns in my dataset"
)

# Continue analysis in the same thread
response = client.add_cell(
    thread.id,
    "Focus on the largest connected component"
)

# Response types vary based on the query
if response.type == "TextElement":
    print(response.text)
elif response.type == "GraphElement":
    print(f"Visualization available at: {response.dataset_id}")
```

### Simple One-Shot Queries

```python
# For quick queries without maintaining thread context
response = client.ask("Summarize the key findings")
print(response.text)
```

### Custom Server URL

```python
# Use a different Louie.ai endpoint
client = louieai.LouieClient(server_url="https://custom.louie.ai")
```

### Managing Threads

```python
# List existing threads
threads = client.list_threads(page_size=10)
for thread in threads:
    print(f"{thread.id}: {thread.name}")

# Continue an existing thread
if threads:
    response = client.add_cell(
        threads[0].id,
        "What were the main conclusions?"
    )
```

### Error Handling

```python
try:
    thread = client.create_thread(
        initial_prompt="Query the sales database"
    )
    response = client.add_cell(thread.id, "Show top customers")
except RuntimeError as e:
    if "No Graphistry API token" in str(e):
        print("Please authenticate with graphistry.register() first")
    elif "API returned error" in str(e):
        print(f"Server error: {e}")
    elif "Failed to connect" in str(e):
        print(f"Network error: {e}")
```

## Common Issues

### Authentication Errors

If you see "No Graphistry API token found", ensure you've called `graphistry.register()` with valid credentials before creating the LouieClient.

### Network Errors

Network errors are wrapped in `RuntimeError` with descriptive messages. Check your internet connection and verify the server URL is accessible.

### API Errors

HTTP errors from the API include the status code and any error message from the server response.