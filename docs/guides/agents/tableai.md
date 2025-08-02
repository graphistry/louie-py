# TableAI Agent Guide

The TableAI agent provides intelligent table analysis and insights, automatically discovering patterns, anomalies, and relationships in tabular data.

## Overview

- **TableAIAgent** - AI-powered table analysis and insights generation

## TableAIAgent

The TableAIAgent understands:
- Data types and distributions
- Statistical patterns
- Anomalies and outliers
- Relationships between columns
- Business context and meaning

### Basic Usage

```python
from louieai.notebook import lui

# Basic analysis
lui("Analyze this sales data table", agent="TableAIAgent")

# Find patterns
lui("What patterns do you see in this customer data?", agent="TableAIAgent")

# Anomaly detection
lui("Find any unusual values or outliers in this dataset", agent="TableAIAgent")
```

### Data Profiling

```python
# Comprehensive profiling
lui("""
Profile this dataset including:
- Column statistics
- Data types and formats
- Missing value patterns
- Unique value counts
- Distribution characteristics
""", agent="TableAIAgent")

# Quality assessment
lui("""
Assess data quality:
- Completeness scores
- Consistency checks
- Accuracy indicators
- Duplicate detection
- Format validation
""", agent="TableAIAgent")

# Business rules validation
lui("""
Check if data follows business rules:
- Prices should be positive
- Dates should be in valid range
- Email formats should be valid
- Referential integrity
""", agent="TableAIAgent")
```

### Pattern Discovery

```python
# Correlation analysis
lui("""
Find correlations and relationships:
- Between numeric columns
- Categorical associations
- Time-based patterns
- Hidden dependencies
""", agent="TableAIAgent")

# Trend analysis
lui("""
Analyze trends in this data:
- Growth patterns
- Seasonal variations
- Cyclical behaviors
- Change points
""", agent="TableAIAgent")

# Segmentation
lui("""
Identify natural segments:
- Customer groups
- Behavioral patterns
- Value-based clusters
- Risk categories
""", agent="TableAIAgent")
```

### Anomaly Detection

```python
# Outlier identification
lui("""
Find outliers and anomalies:
- Statistical outliers
- Business rule violations
- Unusual combinations
- Temporal anomalies
""", agent="TableAIAgent")

# Fraud indicators
lui("""
Look for potential fraud patterns:
- Unusual transaction amounts
- Suspicious timing patterns
- Account behavior changes
- Network anomalies
""", agent="TableAIAgent")

# Data drift
lui("""
Detect data drift:
- Distribution changes
- New categories appearing
- Shift in relationships
- Concept drift
""", agent="TableAIAgent")
```

### Predictive Insights

```python
# Feature importance
lui("""
Which columns are most predictive of:
- Customer churn
- Sales success
- Risk levels
- Future outcomes
""", agent="TableAIAgent")

# Forecast potential
lui("""
Assess forecasting potential:
- Time series patterns
- Seasonality strength
- Trend stability
- Predictability score
""", agent="TableAIAgent")

# Recommendation generation
lui("""
Generate recommendations:
- Data collection improvements
- Feature engineering ideas
- Analysis next steps
- Business actions
""", agent="TableAIAgent")
```

## Common Use Cases

### Business Intelligence

```python
# KPI analysis
lui("""
Analyze key business metrics:
- Revenue drivers
- Cost factors
- Efficiency metrics
- Growth indicators
""", agent="TableAIAgent")

# Customer insights
lui("""
Extract customer insights:
- Lifetime value patterns
- Churn indicators
- Engagement levels
- Satisfaction drivers
""", agent="TableAIAgent")

# Product analysis
lui("""
Analyze product performance:
- Best sellers
- Profit margins
- Return rates
- Cross-sell patterns
""", agent="TableAIAgent")
```

### Financial Analysis

```python
# Transaction analysis
lui("""
Analyze financial transactions:
- Spending patterns
- Risk indicators
- Fraud signals
- Category trends
""", agent="TableAIAgent")

# Portfolio assessment
lui("""
Assess portfolio characteristics:
- Risk distribution
- Return patterns
- Diversification
- Correlation analysis
""", agent="TableAIAgent")

# Budget analysis
lui("""
Analyze budget data:
- Variance analysis
- Overspending patterns
- Efficiency opportunities
- Forecast accuracy
""", agent="TableAIAgent")
```

### Operational Analytics

```python
# Process mining
lui("""
Analyze process data:
- Bottlenecks
- Cycle times
- Process variants
- Efficiency gaps
""", agent="TableAIAgent")

# Quality control
lui("""
Analyze quality metrics:
- Defect patterns
- Root causes
- Process stability
- Improvement areas
""", agent="TableAIAgent")

# Resource utilization
lui("""
Analyze resource usage:
- Capacity patterns
- Utilization rates
- Peak periods
- Optimization opportunities
""", agent="TableAIAgent")
```

## Advanced Analysis

### Multi-table Analysis

```python
# Relationship discovery
lui("""
Analyze relationships across tables:
- Foreign key relationships
- Hidden connections
- Data lineage
- Impact analysis
""", agent="TableAIAgent")

# Cross-table patterns
lui("""
Find patterns across multiple tables:
- Consistent behaviors
- Conflicting data
- Missing relationships
- Integration opportunities
""", agent="TableAIAgent")
```

### Time-based Analysis

```python
# Temporal patterns
lui("""
Analyze time-based patterns:
- Daily/weekly cycles
- Monthly variations
- Yearly trends
- Event impacts
""", agent="TableAIAgent")

# Change detection
lui("""
Detect significant changes:
- Trend breaks
- Level shifts
- Volatility changes
- Regime changes
""", agent="TableAIAgent")
```

### Comparative Analysis

```python
# A/B test analysis
lui("""
Analyze A/B test results:
- Statistical significance
- Effect sizes
- Segment differences
- Recommendation
""", agent="TableAIAgent")

# Cohort comparison
lui("""
Compare cohorts:
- Behavioral differences
- Performance variations
- Retention patterns
- Value differences
""", agent="TableAIAgent")
```

## Integration with Other Agents

```python
# Get data from database
lui("Extract customer transaction data", agent="PostgresAgent")
transaction_data = lui.df

# Analyze with TableAI
lui("""
Analyze this transaction data for:
- Spending patterns
- Customer segments
- Anomalies
- Predictive features
""", agent="TableAIAgent")

# Visualize findings
lui("Create visualizations of the key findings", agent="PerspectiveAgent")

# Generate report
lui("Write an executive summary of the analysis", agent="TextAgent")
```

## Best Practices

### Data Preparation

```python
# Preprocessing guidance
lui("""
Suggest data preparation steps:
- Cleaning requirements
- Transformation needs
- Feature engineering
- Sampling strategy
""", agent="TableAIAgent")
```

### Analysis Strategy

```python
# Analysis roadmap
lui("""
Create analysis plan for this data:
- Priority analyses
- Key questions
- Method selection
- Success metrics
""", agent="TableAIAgent")
```

### Interpretation

```python
# Business context
lui("""
Interpret findings in business context:
- What does this mean?
- Why does it matter?
- What actions to take?
- Expected impact?
""", agent="TableAIAgent")
```

## Output Formats

### Summary Reports

```python
# Executive summary
lui("""
Create executive summary:
- Key findings
- Critical insights
- Recommendations
- Next steps
""", agent="TableAIAgent")
```

### Detailed Analysis

```python
# Technical report
lui("""
Generate detailed report:
- Methodology
- Statistical results
- Visualizations
- Confidence levels
""", agent="TableAIAgent")
```

### Action Items

```python
# Actionable insights
lui("""
List actionable insights:
- Immediate actions
- Investigation areas
- Monitoring needs
- Process improvements
""", agent="TableAIAgent")
```

## Next Steps

- Learn about [Perspective Agent](perspective.md) for interactive table visualization
- Explore [Code Agent](code.md) for advanced analysis scripts
- See [PostgreSQL Agent](postgresql.md) for database integration
- Check the [Query Patterns Guide](../query-patterns.md) for more examples