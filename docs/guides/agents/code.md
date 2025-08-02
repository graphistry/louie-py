# Code Agent Guide (Python)

The Code agents help you generate, analyze, and execute Python code for data processing, automation, and analysis tasks.

## Overview

- **CodeAgent** - AI-powered code generation with explanations
- **CodePassthroughAgent** - Direct code execution without AI modification

## CodeAgent (AI-Assisted)

The CodeAgent understands:
- Data science libraries (pandas, numpy, scikit-learn)
- Visualization tools (matplotlib, seaborn, plotly)
- Common programming patterns
- Your data context from previous queries

### Basic Usage

```python
from louieai.notebook import lui

# Data processing
lui("Write code to clean this dataframe by removing duplicates and null values", 
    agent="CodeAgent")

# Analysis functions
lui("Create a function to calculate moving averages with different windows", 
    agent="CodeAgent")

# Visualization
lui("Generate code to create a dashboard with these metrics", 
    agent="CodeAgent")
```

### Data Analysis Code

```python
# Statistical analysis
lui("""
Write code to perform statistical analysis on this dataset including:
- Descriptive statistics
- Correlation analysis  
- Outlier detection using IQR method
""", agent="CodeAgent")

# Machine learning
lui("""
Create a complete machine learning pipeline to predict customer churn
including data preprocessing, feature engineering, model training,
and evaluation
""", agent="CodeAgent")

# Time series analysis
lui("""
Generate code for time series analysis including:
- Trend decomposition
- Seasonality detection
- ARIMA forecasting
""", agent="CodeAgent")
```

### Data Processing Pipelines

```python
# ETL pipeline
lui("""
Write a data pipeline that:
1. Reads data from multiple CSV files
2. Cleans and standardizes the data
3. Performs aggregations
4. Saves results to parquet format
""", agent="CodeAgent")

# Real-time processing
lui("""
Create code to process streaming data that:
- Validates incoming records
- Applies transformation rules
- Detects anomalies in real-time
- Sends alerts for critical events
""", agent="CodeAgent")

# Batch processing
lui("""
Generate an efficient batch processing script that handles
millions of records with proper error handling and logging
""", agent="CodeAgent")
```

### Automation Scripts

```python
# Report generation
lui("""
Write code to automatically generate a weekly report that:
- Pulls data from our database
- Creates visualizations
- Generates a PDF with insights
- Emails to stakeholders
""", agent="CodeAgent")

# Data quality monitoring
lui("""
Create a monitoring script that checks data quality daily
and sends alerts when issues are detected
""", agent="CodeAgent")

# API integration
lui("""
Generate code to integrate with external APIs, handle
rate limiting, retry logic, and error handling
""", agent="CodeAgent")
```

## CodePassthroughAgent (Direct Execution)

For direct code execution without AI modification:

### Basic Execution

```python
# Direct Python execution
lui("""
import pandas as pd
import numpy as np

# Load and process data
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=100),
    'value': np.random.randn(100).cumsum() + 100
})

# Calculate metrics
df['rolling_mean'] = df['value'].rolling(window=7).mean()
df['rolling_std'] = df['value'].rolling(window=7).std()

print(df.describe())
""", agent="CodePassthroughAgent")
```

### Advanced Data Processing

```python
# Complex transformations
lui("""
def process_customer_data(df):
    # Customer segmentation
    df['total_spent'] = df.groupby('customer_id')['amount'].transform('sum')
    df['order_count'] = df.groupby('customer_id')['order_id'].transform('count')
    df['avg_order_value'] = df['total_spent'] / df['order_count']
    
    # RFM analysis
    current_date = df['order_date'].max()
    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (current_date - x.max()).days,  # Recency
        'order_id': 'count',  # Frequency  
        'amount': 'sum'  # Monetary
    }).reset_index()
    
    # Segment customers
    rfm['segment'] = pd.qcut(rfm['amount'], q=4, labels=['Low', 'Medium', 'High', 'VIP'])
    
    return rfm

# Execute on actual data
result = process_customer_data(customer_df)
print(result.head())
""", agent="CodePassthroughAgent")
```

### Custom Visualizations

```python
# Advanced plotting
lui("""
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec

# Create figure with custom layout
fig = plt.figure(figsize=(15, 10))
gs = GridSpec(3, 3, figure=fig)

# Time series plot
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(df['date'], df['value'], label='Original')
ax1.plot(df['date'], df['rolling_mean'], label='7-day MA', linewidth=2)
ax1.fill_between(df['date'], 
                 df['rolling_mean'] - df['rolling_std'],
                 df['rolling_mean'] + df['rolling_std'], 
                 alpha=0.3)
ax1.set_title('Time Series with Moving Average')
ax1.legend()

# Distribution plot
ax2 = fig.add_subplot(gs[1, 0])
sns.histplot(df['value'], kde=True, ax=ax2)
ax2.set_title('Value Distribution')

# Correlation heatmap
ax3 = fig.add_subplot(gs[1, 1:])
corr_matrix = df[['value', 'rolling_mean', 'rolling_std']].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax3)
ax3.set_title('Correlation Matrix')

plt.tight_layout()
plt.show()
""", agent="CodePassthroughAgent")
```

## Best Practices

### When to Use Each Agent

**Use CodeAgent when:**
- You need code explained with comments
- You want best practices and error handling included
- You're learning or need code documentation
- You want optimized, production-ready code

**Use CodePassthroughAgent when:**
- You have exact code to execute
- You're testing specific implementations
- You need direct control over execution
- You're debugging existing code

### Error Handling Patterns

```python
# AI adds comprehensive error handling
lui("""
Write code to process user uploads with proper validation
and error handling
""", agent="CodeAgent")

# Direct implementation with specific error handling
lui("""
def safe_process_file(filepath):
    try:
        # Validate file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        # Check file size
        file_size = os.path.getsize(filepath)
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError(f"File too large: {file_size} bytes")
            
        # Process based on type
        if filepath.endswith('.csv'):
            return pd.read_csv(filepath)
        elif filepath.endswith('.json'):
            return pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file type: {filepath}")
            
    except Exception as e:
        logger.error(f"Error processing {filepath}: {str(e)}")
        raise
        
result = safe_process_file('data.csv')
""", agent="CodePassthroughAgent")
```

## Common Patterns

### Data Science Workflows

```python
# AI generates complete workflow
lui("""
Create a complete data science workflow for predicting
customer lifetime value including EDA, feature engineering,
model selection, and evaluation
""", agent="CodeAgent")

# Execute specific model
lui("""
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

# Prepare features
X = df[['recency', 'frequency', 'monetary', 'tenure']]
y = df['lifetime_value']

# Train model with cross-validation
model = RandomForestRegressor(n_estimators=100, random_state=42)
scores = cross_val_score(model, X, y, cv=5, scoring='r2')

print(f"R² scores: {scores}")
print(f"Average R²: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")

# Feature importance
model.fit(X, y)
importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(importance)
""", agent="CodePassthroughAgent")
```

### Performance Optimization

```python
# AI suggests optimized code
lui("""
Optimize this data processing code to handle millions
of records efficiently
""", agent="CodeAgent")

# Direct optimized implementation
lui("""
import numpy as np
from numba import jit
import dask.dataframe as dd

@jit(nopython=True)
def fast_calculate(values):
    result = np.empty_like(values)
    for i in range(len(values)):
        # Complex calculation
        result[i] = np.sqrt(values[i] ** 2 + values[i])
    return result

# Process large dataset in chunks
def process_large_file(filename, chunksize=10000):
    processed_chunks = []
    
    for chunk in pd.read_csv(filename, chunksize=chunksize):
        # Apply optimized function
        chunk['calculated'] = fast_calculate(chunk['value'].values)
        processed_chunks.append(chunk)
    
    return pd.concat(processed_chunks, ignore_index=True)

# Or use Dask for parallel processing
ddf = dd.read_csv('large_file.csv')
result = ddf.map_partitions(lambda df: df.assign(
    calculated=fast_calculate(df['value'].values)
)).compute()
""", agent="CodePassthroughAgent")
```

## Integration with Other Agents

```python
# Get data from database
lui("Fetch customer transaction data from last month", agent="PostgresAgent")
transaction_df = lui.df

# Generate analysis code
lui("""
Write code to analyze these transactions for:
- Fraud detection patterns
- Customer segmentation
- Revenue forecasting
""", agent="CodeAgent")

# Visualize results
lui("Create an interactive dashboard of the analysis results", agent="GraphAgent")

# Generate report
lui("Create a PDF report summarizing all findings", agent="CodeAgent")
```

## Testing and Validation

```python
# AI generates tests
lui("""
Write unit tests for the data processing functions
including edge cases and error conditions
""", agent="CodeAgent")

# Direct test implementation
lui("""
import pytest
import pandas as pd
from unittest.mock import Mock, patch

class TestDataProcessor:
    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = process_data(df)
        assert result.empty
        
    def test_missing_values(self):
        df = pd.DataFrame({'value': [1, None, 3, None, 5]})
        result = clean_data(df)
        assert result['value'].isna().sum() == 0
        
    def test_performance(self):
        # Generate large test dataset
        large_df = pd.DataFrame({
            'id': range(1000000),
            'value': np.random.randn(1000000)
        })
        
        import time
        start = time.time()
        result = process_data(large_df)
        duration = time.time() - start
        
        assert duration < 5.0  # Should complete within 5 seconds
        assert len(result) == len(large_df)

# Run tests
pytest.main([__file__, '-v'])
""", agent="CodePassthroughAgent")
```

## Next Steps

- Learn about [Graph Agent](graph.md) for visualizations
- Explore other agents in the [Agents Reference](../../reference/agents.md)
- Check the [Query Patterns Guide](../query-patterns.md) for more examples