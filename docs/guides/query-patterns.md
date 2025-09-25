# Query Patterns

This guide covers common query patterns for effective use of LouieAI.

## Basic Query Structure

LouieAI accepts natural language queries that can include:
- Direct questions about your data
- Analysis requests
- Visualization instructions
- Multi-step investigation workflows

## Query Types

### Data Exploration
- "Show me the schema of the users table"
- "What data sources are available?"
- "Summarize the customer_transactions dataset"

### Analysis Queries
- "Find anomalies in the transaction data from last week"
- "Calculate the conversion rate by marketing channel"
- "Identify the top 10 customers by revenue"

### Visualization Requests
- "Create a graph showing user connections"
- "Plot sales trends over the last 6 months"
- "Show me a heatmap of activity by hour and day of week"

### Investigation Workflows
- "Investigate suspicious login patterns for user X"
- "Trace the flow of funds from account A to account B"
- "Find all related entities connected to IP address Y"

## Best Practices

1. **Be Specific**: Include relevant details like time ranges, entity names, or specific metrics
2. **Provide Context**: Mention the goal of your analysis to get more targeted results
3. **Iterate**: Start with broad queries and refine based on initial results
4. **Use Domain Language**: Use terminology specific to your data and business domain

## Advanced Patterns

### Combining Multiple Operations
```python
lui("Find high-value transactions from last month, then visualize the network of entities involved, and identify any suspicious patterns")
```

### Conditional Analysis
```python
lui("If there are more than 100 failed login attempts today, show me the geographic distribution and identify potential attack patterns")
```

### Comparative Analysis
```python
lui("Compare this week's sales performance to the same week last year, highlighting significant changes")
```

## Working with Results

Access previous results using the cursor history:
```python
# Get dataframe from previous query
df = lui[-1].df

# Access multiple past results
for response in lui.history[-5:]:
    print(response.text)
```

## DataFrame Analysis Patterns

### Uploading Your Data

Analyze your own pandas DataFrames using natural language:

```python
import pandas as pd

# Load your data
df = pd.read_csv("data.csv")

# Basic analysis
lui("What insights can you find?", df)

# Specific questions
lui("Which columns have missing values?", df)
lui("Show correlation between features", df)
lui("Identify outliers in the sales column", df)
```

### Common DataFrame Operations

```python
# Statistical analysis
lui("Calculate descriptive statistics", df)
lui("Show distribution of values by category", df)

# Data quality checks
lui("Check for data quality issues", df)
lui("Find duplicate rows", df)

# Transformations
lui("Normalize the numeric columns", df)
lui("Create pivot table by region and product", df)

# Time series analysis (if datetime column exists)
lui("Analyze trends over time", df)
lui("Detect seasonality patterns", df)
lui("Forecast next 30 days", df)
```

### Combining Multiple DataFrames

```python
# Analyze first dataset
lui("Profile this customer data", customers_df)

# Add related data for deeper analysis
lui("Now analyze purchase patterns", purchases_df)

# Ask questions across both datasets
lui("Which customer segments have highest lifetime value?")
```

## See Also
- [Agent Selection](agent-selection.md) - Choose the right agents for your queries
- [Examples](examples.md) - More detailed examples
- [API Reference](../api/notebook.md) - Technical details