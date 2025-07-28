# Roleplay: Data Analyst Using Louie.ai Python Client

**Persona**: Mike, Data Analyst at an e-commerce company
**Goal**: Analyze sales trends and customer behavior across multiple databases
**Context**: V1 minimal Python client for business intelligence tasks

---

**Mike**: I need to analyze our Q4 sales data. Let me set up the Louie client in my Jupyter notebook.

**Louie Docs**: Start by importing and authenticating:
```python
import pandas as pd
import graphistry
from louieai import LouieClient

# Use environment variables for credentials
graphistry.register(api=3, username=os.getenv("GRAPHISTRY_USER"), password=os.getenv("GRAPHISTRY_PASS"))
client = LouieClient()
```

**Mike**: I'll create a thread for this quarterly analysis. Can I add metadata?

**Louie Docs**: Yes, you can name your thread for organization:
```python
analysis_thread = client.create_thread(
    name="Q4 2024 Sales Analysis",
    description="Quarterly sales trends and customer segmentation"  # if supported
)
```

**Mike**: Let me start by querying our ClickHouse data warehouse for sales by category.

**Louie Docs**: Add your analytical query as a cell:
```python
sales_response = client.add_cell(
    thread_id=analysis_thread.id,
    content="""
    Query ClickHouse for Q4 2024 sales:
    - Group by product category
    - Include revenue, units sold, and average order value
    - Compare with Q4 2023
    """
)

sales_df = sales_response.to_dataframe()
print(f"Retrieved {len(sales_df)} categories")
```

**Mike**: Can I pass the results from one query to another? I want to deep dive into the top performing categories.

**Louie Docs**: Yes, reference previous results in follow-up queries:
```python
# Identify top 5 categories
top_categories = sales_df.nlargest(5, 'revenue')['category'].tolist()

# Deep dive into customer segments
segment_response = client.add_cell(
    thread_id=analysis_thread.id,
    content=f"""
    For categories {top_categories}, query PostgreSQL to analyze:
    - Customer demographics
    - Repeat purchase rate
    - Geographic distribution
    Use the customer_orders and customer_profiles tables
    """
)

segment_df = segment_response.to_dataframe()
```

**Mike**: I'm getting a lot of data. Can Louie help me identify key insights?

**Louie Docs**: Ask Louie to analyze patterns and anomalies:
```python
insights_response = client.add_cell(
    thread_id=analysis_thread.id,
    content="""
    Analyze the sales and customer data to identify:
    1. Most significant trends compared to last year
    2. Unexpected patterns or anomalies
    3. Customer segments with highest growth potential
    Provide actionable insights for the business team
    """
)

print(insights_response.content)  # Natural language insights
```

**Mike**: How do I know what databases and tables are available to query?

**Louie Docs**: Ask Louie about available data sources:
```python
schema_response = client.add_cell(
    thread_id=analysis_thread.id,
    content="List available databases and main tables for sales analysis"
)

print(schema_response.content)
# Output might include: ClickHouse (sales_fact, product_dim), PostgreSQL (customers, orders), etc.
```

**Mike**: Can I combine data from multiple databases in one query?

**Louie Docs**: Yes, Louie can orchestrate cross-database queries:
```python
combined_response = client.add_cell(
    thread_id=analysis_thread.id,
    content="""
    Combine data from:
    - ClickHouse: sales_fact table for transaction data
    - PostgreSQL: customer_profiles for demographics
    - OpenSearch: website_events for browsing behavior
    
    Join on customer_id and analyze conversion patterns
    """
)

combined_df = combined_response.to_dataframe()
```

**Mike**: I need to create a report. Can I get visualizations?

**Louie Docs**: In V1, focus on data retrieval. For now, create visualizations locally:
```python
# Get the data
viz_data = combined_df

# Create your own visualizations
import matplotlib.pyplot as plt
import seaborn as sns

# Louie V2 will support: "Create a bar chart of sales by category"
# For now, do it manually with the DataFrame
```

**Mike**: How do I monitor long-running queries?

**Louie Docs**: Check response status for long queries:
```python
# For potentially long queries
big_response = client.add_cell(
    thread_id=analysis_thread.id,
    content="Calculate customer lifetime value for all 2M+ customers in the past 5 years"
)

# Check status
if big_response.status == "running":
    print("Query still running...")
    # In V1, you might need to poll or wait
    
# Better pattern for V1
import time
while big_response.status == "running":
    time.sleep(5)
    big_response = client.get_cell_status(analysis_thread.id, big_response.cell_id)
```

**Mike**: Perfect! Let me save my analysis for the team meeting.

**Louie Docs**: Export your complete analysis:
```python
# Save all DataFrames
sales_df.to_excel("q4_analysis.xlsx", sheet_name="Sales", index=False)
segment_df.to_excel("q4_analysis.xlsx", sheet_name="Segments", index=False)

# Save the analysis narrative
with open("q4_insights.md", "w") as f:
    f.write(f"# Q4 2024 Analysis\n\n")
    f.write(f"Thread ID: {analysis_thread.id}\n\n")
    f.write(insights_response.content)
```

---

## Key Documentation Needs Identified

1. **Jupyter Integration**: Common patterns for notebook usage
2. **Complex Queries**: Multi-line queries with specific requirements
3. **Data Source Discovery**: How to explore available databases/tables
4. **Cross-Database Joins**: Orchestrating queries across systems
5. **Result Chaining**: Using outputs from one query in another
6. **Status Monitoring**: Handling long-running analytical queries
7. **Export Patterns**: Saving results in business-friendly formats
8. **V1 Limitations**: Clear about what requires local processing (like viz)