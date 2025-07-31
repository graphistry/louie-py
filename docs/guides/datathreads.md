# Working with DataThreads

DataThreads are LouieAI's way of maintaining conversational context across multiple queries. Think of them as persistent chat sessions where Louie remembers your previous questions and responses.

## What are DataThreads?

A datathread is a conversational session that:
- **Maintains context** across multiple queries
- **Stores artifacts** like generated DataFrames and visualizations
- **Remembers previous analysis** for follow-up questions
- **Can be resumed** later or shared with others

## Creating and Using DataThreads

### Simple Thread Creation

```python
import graphistry
import louieai as lui

# Set up authentication
graphistry.register(api=3, server="hub.graphistry.com", username="your_user", password="your_pass")
client = lui.LouieClient(server_url="https://den.louie.ai")

# Create a new thread with an initial query
thread = client.create_thread(
    name="Sales Analysis", 
    initial_prompt="Load the Q4 sales data and show me the top 10 products"
)

print(f"Created thread: {thread.id}")
```

### Adding Cells to Threads

```python
# Continue the conversation by adding cells
response1 = client.add_cell(thread.id, "Which regions had the highest sales?")
response2 = client.add_cell(thread.id, "Create a visualization comparing regions")
response3 = client.add_cell(thread.id, "What trends do you see month-over-month?")

# Each query builds on the previous context
```

### Creating Threads Without Initial Prompts

```python
# Create an empty thread first
thread = client.create_thread(name="Customer Analysis")

# Then add your first query
response = client.add_cell(thread.id, "Load customer data from last quarter")
```

### One-Shot Queries (Auto-Thread Creation)

For quick queries, LouieAI can automatically create threads:

```python
# Pass empty string as thread_id to auto-create
response = client.add_cell("", "Show me a summary of recent security incidents")
print(f"Auto-created thread: {response.thread_id}")

# Continue in the same auto-created thread
followup = client.add_cell(response.thread_id, "Which incidents were critical?")
```

## Managing Multiple DataThreads

### Listing Your Threads

```python
# Get recent threads
threads = client.list_threads(page=1, page_size=10)

for thread in threads:
    print(f"Thread {thread.id}: {thread.name}")
    print(f"  Created: {thread.created_at}")
    print(f"  Updated: {thread.updated_at}")
```

### Switching Between Threads

```python
# Work on multiple analyses simultaneously
sales_thread = client.create_thread(name="Sales Analysis")
security_thread = client.create_thread(name="Security Review")

# Add queries to different threads
client.add_cell(sales_thread.id, "Show me revenue trends")
client.add_cell(security_thread.id, "Analyze recent login failures")

# Switch back to sales analysis
client.add_cell(sales_thread.id, "Break down revenue by product category")
```

### Retrieving Thread Information

```python
# Get details about a specific thread
thread = client.get_thread("D_thread001")
print(f"Thread: {thread.name}")
print(f"ID: {thread.id}")
```

## Working with Artifacts

DataThreads automatically store artifacts (results) from your queries. Here's how to access them:

### Text Responses

```python
response = client.add_cell(thread.id, "Summarize the key findings")

# Access text content
for text_elem in response.text_elements:
    print("Analysis:")
    print(text_elem['text'])
    print("Language:", text_elem.get('language', 'Markdown'))
```

### DataFrames

```python
response = client.add_cell(thread.id, "Create a table of top customers by revenue")

# Access generated DataFrames
for df_elem in response.dataframe_elements:
    df = df_elem['table']  # This is a pandas DataFrame
    print(f"DataFrame shape: {df.shape}")
    print(df.head())
    
    # You can work with it like any pandas DataFrame
    top_customers = df.head(5)
    total_revenue = df['revenue'].sum()
```

### Visualizations

```python
response = client.add_cell(thread.id, "Create a network graph of customer relationships")

# Check for generated visualizations
if response.has_graphs:
    for graph_elem in response.graph_elements:
        print(f"Graph ID: {graph_elem['dataset_id']}")
        print(f"Status: {graph_elem['status']}")
        # The graph is automatically displayed in Graphistry
```

### Mixed Response Types

Many queries return multiple types of artifacts:

```python
response = client.add_cell(thread.id, "Analyze customer churn and create both a summary table and visualization")

# Handle all response types
print("=== Text Analysis ===")
for text in response.text_elements:
    print(text['text'])

print("=== Data Tables ===")
for df_elem in response.dataframe_elements:
    print(f"Table with {len(df_elem['table'])} rows")

print("=== Visualizations ===")
if response.has_graphs:
    print(f"Created {len(response.graph_elements)} visualizations")
```

## Best Practices

### Naming Threads Meaningfully

```python
# Good: Descriptive names
client.create_thread(name="Q4 2024 Sales Performance Analysis")
client.create_thread(name="Security Incident Investigation - Dec 2024")

# Less helpful: Generic names
client.create_thread(name="Analysis")
client.create_thread(name="Thread 1")
```

### Building Context Progressively

```python
# Start broad, then get specific
thread = client.create_thread(name="Customer Segmentation")

# Step 1: Load and explore
client.add_cell(thread.id, "Load customer data and show me an overview")

# Step 2: Segment  
client.add_cell(thread.id, "Segment customers by purchase behavior")

# Step 3: Analyze
client.add_cell(thread.id, "Which segment has the highest lifetime value?")

# Step 4: Actionable insights
client.add_cell(thread.id, "What marketing strategies would work best for each segment?")
```

### Error Handling

```python
try:
    response = client.add_cell(thread.id, "Complex analysis query")
    
    # Check for errors in the response
    if response.has_errors:
        print("Query completed with errors:")
        for elem in response.elements:
            if elem.get('type') == 'ExceptionElement':
                print(f"Error: {elem.get('message', 'Unknown error')}")
    else:
        # Process successful results
        for text in response.text_elements:
            print(text['text'])
            
except Exception as e:
    print(f"Request failed: {e}")
```

## Common Patterns

### Data Exploration Flow

```python
thread = client.create_thread(name="Dataset Exploration")

# 1. Overview
client.add_cell(thread.id, "Load the dataset and give me an overview")

# 2. Data quality
client.add_cell(thread.id, "Check for missing values and data quality issues")

# 3. Distributions
client.add_cell(thread.id, "Show me the distribution of key variables")

# 4. Correlations
client.add_cell(thread.id, "What are the strongest correlations in the data?")
```

### Investigation Workflow

```python
thread = client.create_thread(name="Security Investigation")

# 1. Scope the issue
client.add_cell(thread.id, "Show me all failed login attempts from the last 24 hours")

# 2. Pattern analysis
client.add_cell(thread.id, "Group these by IP address and look for patterns")

# 3. Threat assessment
client.add_cell(thread.id, "Which IPs show signs of brute force attacks?")

# 4. Impact analysis
client.add_cell(thread.id, "Were any of these attacks successful?")
```

## Next Steps

- **[Query Patterns](query-patterns.md)** - Advanced query techniques for orchestration and specialized agents
- **[Examples](examples.md)** - More practical examples and use cases
- **[Authentication Guide](authentication.md)** - Multi-tenant and advanced authentication setups