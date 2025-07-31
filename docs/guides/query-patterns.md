# Query Pattern Library

This library demonstrates the full power of Louie.ai through natural language queries. With just the `add_cell` method, you can access all of Louie's capabilities.

## Getting Started

```python
import graphistry
from louieai import LouieClient

# Authenticate with Graphistry
graphistry.register(api=3, username="your_user", password="your_pass")

# Create Louie client
client = LouieClient()

# Start a new analysis thread
thread = client.create_thread(name="Customer Analysis")
```

## Table of Contents

1. [Database Queries](#database-queries)
2. [Visualizations](#visualizations)
3. [Analysis & Insights](#analysis-insights)
4. [Multi-Step Workflows](#multi-step-workflows)
5. [Data Integration](#data-integration)
6. [Orchestration Agents](#orchestration-agents)
7. [Specialized Tools & Agents](#specialized-tools-agents)
8. [Advanced Patterns](#advanced-patterns)

## Database Queries

### Single Database Query
```python
# Create thread and query PostgreSQL
thread = client.create_thread(
    name="Customer Query",
    initial_prompt="Query PostgreSQL customers table for users who signed up in the last 30 days"
)

# Access the response (thread was created with initial_prompt)
response = thread  # Initial response is returned when thread is created

# If response contains data
if hasattr(response, 'to_dataframe'):
    df = response.to_dataframe()
```

### Complex SQL with Aggregations
```python
# ClickHouse analytics
response = client.add_cell(thread.id, """
    Query ClickHouse to calculate:
    - Total revenue by product category for Q4
    - Month-over-month growth rate
    - Top 10 products by revenue
    Group by category and month
""")
```

### Log Search
```python
# Splunk search
response = client.add_cell(thread.id, 
    "Search Splunk for failed login attempts in the last 24 hours from IP addresses outside the US"
)

# OpenSearch query
response = client.add_cell(thread.id,
    "Find all error logs in OpenSearch where the error message contains 'timeout' and service='payment-api'"
)
```

### Graph Database Query
```python
# Kusto graph query
response = client.add_cell(thread.id,
    "Query Kusto to find all connections between user123 and any flagged accounts within 3 hops"
)
```

## Visualizations

### Network Graphs with Graphistry
```python
# User behavior network
response = client.add_cell(thread.id, """
    Create a Graphistry visualization showing:
    - All users who purchased product X
    - Their connections through shared attributes (email domain, IP, device)
    - Color nodes by risk score
    - Size by transaction volume
""")

if response.dataset_id:
    print(f"View graph: https://hub.graphistry.com/graph/graph.html?dataset={response.dataset_id}")
```

### UMAP Clustering Visualization
```python
# Customer segmentation
response = client.add_cell(thread.id, """
    Create a UMAP visualization of customer segments based on:
    - Purchase history
    - Browsing behavior  
    - Demographics
    Color by customer lifetime value
""")
```

### Geographic Visualization with Kepler
```python
# Delivery optimization
response = client.add_cell(thread.id, """
    Create a Kepler map showing:
    - All deliveries in the last week
    - Color routes by delivery time vs SLA
    - Add heatmap layer for delivery density
    - Include warehouse locations as points
""")
```

### Interactive Charts with Perspective
```python
# Sales dashboard
response = client.add_cell(thread.id, """
    Create a Perspective heatmap showing:
    - Sales by region (rows) and product category (columns)
    - Values as revenue
    - Include quarterly comparison
    Make it interactive with drill-down capability
""")
```

### Traditional Charts
```python
# Time series analysis
response = client.add_cell(thread.id, """
    Create a matplotlib line chart showing:
    - Daily active users over the last 90 days
    - Add 7-day moving average
    - Highlight weekends
    - Include trend line
""")

# Returns Base64ImageElement
if response.type == "Base64ImageElement":
    # Save or display image
    save_base64_image(response.src, "user_trends.png")
```

## Analysis Insights

### Anomaly Detection with TableAI
```python
# Find unusual patterns
response = client.add_cell(thread.id, """
    Use TableAI to analyze the sales data and:
    - Identify statistical anomalies in transaction amounts
    - Find unusual purchasing patterns
    - Highlight suspicious customer behaviors
    Explain why each anomaly is significant
""")
```

### Correlation Analysis
```python
# Multi-factor analysis
response = client.add_cell(thread.id, """
    Analyze correlations between:
    - Marketing spend by channel
    - Website traffic sources
    - Conversion rates
    - Customer acquisition cost
    
    Identify which marketing channels drive the best ROI
""")
```

### Predictive Analysis
```python
# Forecasting
response = client.add_cell(thread.id, """
    Based on historical data:
    - Forecast next quarter's revenue by product line
    - Identify seasonal trends
    - Calculate confidence intervals
    - Highlight risks and opportunities
""")
```

### Natural Language Summaries
```python
# Executive summary
response = client.add_cell(thread.id, """
    Analyze all customer data from the past quarter and provide:
    - Executive summary (3 bullet points)
    - Key trends and changes
    - Actionable recommendations
    - Areas of concern
    Format as a brief report
""")

print(response.content)  # Markdown-formatted insights
```

## Multi-Step Workflows

### Investigation Workflow
```python
# Step 1: Identify suspicious activity
response1 = client.add_cell(thread.id, 
    "Query Splunk for all failed login attempts in the last 48 hours"
)

# Step 2: Enrich with user data
suspicious_ips = response1.to_dataframe()['source_ip'].unique()
response2 = client.add_cell(thread.id, 
    f"For these IPs {suspicious_ips.tolist()}, query the user database to find associated accounts"
)

# Step 3: Visualize attack pattern
response3 = client.add_cell(thread.id,
    "Create a Graphistry timeline visualization showing the attack pattern with IPs and targeted accounts"
)

# Step 4: Generate incident report
response4 = client.add_cell(thread.id,
    "Summarize this security incident with severity assessment and recommended actions"
)
```

### Data Quality Analysis
```python
# Comprehensive data audit
response = client.add_cell(thread.id, """
    Perform a data quality audit across all our databases:
    1. Check for missing values in critical fields
    2. Identify duplicate records
    3. Find referential integrity issues
    4. Detect outliers and anomalies
    5. Create a data quality scorecard
    6. Visualize issues by table and severity
""")

# Single query handles entire workflow
```

## Data Integration

### Cross-Database Joins
```python
# Unified customer view
response = client.add_cell(thread.id, """
    Combine data from multiple sources:
    - PostgreSQL: Customer profiles and preferences
    - ClickHouse: Transaction history and analytics
    - OpenSearch: Support tickets and interactions
    - Splunk: System access logs
    
    Create unified customer profiles for our VIP segment
""")
```

### Real-time + Historical Analysis
```python
# Hybrid analysis
response = client.add_cell(thread.id, """
    Compare real-time metrics with historical patterns:
    - Current traffic from Splunk (last hour)
    - Historical patterns from ClickHouse (same hour, past 30 days)
    - Identify deviations > 2 standard deviations
    - Alert on anomalies with context
""")
```

## Orchestration Agents

Orchestration agents excel at coordinating complex, multi-system workflows and managing sophisticated analysis pipelines. These patterns leverage Louie's ability to reason across multiple data sources and coordinate sequential operations.

### Executive Dashboard Orchestration
```python
# Orchestrate a complete executive dashboard update
response = client.add_cell(thread.id, """
    Act as an executive dashboard orchestrator:
    
    1. **Revenue Metrics**: Query Stripe API and Salesforce for Q4 revenue data
    2. **Customer Health**: Pull NPS scores from survey system and churn metrics from analytics DB
    3. **Operational KPIs**: Get system uptime from monitoring and support ticket volumes from Zendesk
    4. **Market Intelligence**: Analyze competitor pricing from scraped data and industry trends
    5. **Risk Assessment**: Review security incidents and compliance status
    
    Orchestrate all data collection, calculate executive-level KPIs, and generate:
    - Executive summary dashboard with key metrics
    - Red/yellow/green status indicators 
    - Trend analysis with quarter-over-quarter comparisons
    - Action items requiring executive attention
""")
```

### Incident Response Orchestration
```python
# Complex security incident response workflow
response = client.add_cell(thread.id, """
    Act as an incident response orchestrator for potential data breach:
    
    **Phase 1 - Detection & Scoping**:
    - Query SIEM (Splunk) for anomalous access patterns in last 48h
    - Cross-reference with identity management system for affected accounts
    - Pull network logs from security appliances for suspicious traffic
    
    **Phase 2 - Impact Assessment**:
    - Identify all databases/systems accessed by compromised accounts
    - Query audit logs to determine data potentially accessed
    - Calculate blast radius and classify incident severity
    
    **Phase 3 - Response Coordination**:
    - Generate timeline of events with evidence
    - Create Graphistry visualization of attack path
    - Produce incident report with recommended containment actions
    - Prepare compliance notification draft if required
    
    Coordinate all phases automatically and provide comprehensive incident briefing.
""")
```

### Business Intelligence Orchestration
```python
# Weekly business intelligence automation
response = client.add_cell(thread.id, """
    Act as a BI orchestrator for comprehensive weekly business review:
    
    **Sales Performance**:
    - Query CRM for pipeline changes and deal progression
    - Analyze conversion rates by source and sales rep
    - Compare actuals vs targets with variance analysis
    
    **Marketing Effectiveness**:
    - Pull campaign performance from Google Ads, Facebook, LinkedIn
    - Calculate customer acquisition cost by channel
    - Measure attribution and multi-touch journey analysis
    
    **Product Usage**:
    - Query product analytics for feature adoption and user engagement
    - Identify usage patterns and potential churn signals
    - Track product-led growth metrics
    
    **Financial Health**:
    - Calculate cash flow, burn rate, and runway projections
    - Analyze subscription metrics (MRR, churn, expansion)
    - Monitor key financial ratios and trends
    
    Orchestrate all analysis and produce executive-ready business intelligence report.
""")
```

### Data Pipeline Orchestration
```python
# Complex ETL orchestration and validation
response = client.add_cell(thread.id, """
    Orchestrate a comprehensive data pipeline validation and optimization:
    
    **Data Quality Assessment**:
    - Validate data freshness across all source systems
    - Check referential integrity between related tables
    - Identify schema drift and missing data patterns
    
    **Performance Analysis**:
    - Query system logs for pipeline execution times
    - Identify bottlenecks in data transformation steps
    - Analyze resource utilization during peak loads
    
    **Data Lineage Mapping**:
    - Trace data flow from sources through transformations
    - Identify downstream dependencies and impact analysis
    - Document critical data assets and ownership
    
    **Optimization Recommendations**:
    - Suggest pipeline improvements and cost optimizations
    - Recommend data partitioning and indexing strategies
    - Provide capacity planning for expected growth
    
    Coordinate all assessments and deliver comprehensive data architecture review.
""")
```

## Specialized Tools & Agents

Specialized agents focus on domain-specific expertise and leverage particular tools or methodologies for deep analysis in their area of specialization.

### TableAI Analysis Agent
```python
# Advanced statistical analysis with TableAI
response = client.add_cell(thread.id, """
    Act as a TableAI statistical analysis specialist:
    
    Use TableAI's advanced capabilities to:
    - Perform sophisticated anomaly detection on customer transaction data
    - Identify subtle patterns in user behavior that indicate fraud risk
    - Build predictive models for customer lifetime value
    - Generate statistical significance tests for A/B test results
    - Create correlation matrices with feature importance rankings
    
    Provide statistical rigor with confidence intervals, p-values, and effect sizes.
    Explain findings in business terms with actionable recommendations.
""")
```

### Graphistry Network Analysis Agent
```python
# Advanced network analysis with Graphistry
response = client.add_cell(thread.id, """
    Act as a Graphistry network analysis specialist:
    
    Create sophisticated network visualizations to:
    - Map customer relationship networks based on shared attributes (email domains, IP addresses, devices)
    - Identify community structures and influential nodes in social networks
    - Trace money flows and transaction patterns for fraud detection
    - Visualize system dependencies and failure propagation paths
    - Build knowledge graphs connecting entities across multiple data sources
    
    Use advanced Graphistry features like:
    - Dynamic node sizing based on centrality measures
    - Edge bundling for cleaner large-network visualization  
    - Time-based animations showing network evolution
    - Interactive filtering and drill-down capabilities
    
    Provide network science insights with centrality measures and community detection.
""")
```

### UMAP Clustering Specialist
```python
# Advanced dimensionality reduction and clustering
response = client.add_cell(thread.id, """
    Act as a UMAP clustering and dimensionality reduction specialist:
    
    Perform advanced customer segmentation using:
    - UMAP for nonlinear dimensionality reduction preserving local structure
    - Multiple clustering algorithms (HDBSCAN, K-means, Gaussian mixture)
    - Feature engineering from behavioral, demographic, and transactional data
    - Cluster validation using silhouette analysis and stability measures
    
    Create interpretable customer segments with:
    - 2D/3D UMAP visualizations colored by cluster and key attributes
    - Cluster characteristic profiles with statistical significance
    - Actionable marketing strategies for each segment
    - Segment migration analysis over time
    
    Provide mathematical rigor with hyperparameter justification and validation metrics.
""")
```

### Security Analysis Agent
```python
# Specialized cybersecurity analysis
response = client.add_cell(thread.id, """
    Act as a cybersecurity analysis specialist:
    
    Perform comprehensive threat hunting and analysis:
    - Parse and correlate logs from multiple security tools (SIEM, EDR, firewall)
    - Apply MITRE ATT&CK framework to identify attack patterns
    - Use behavioral analytics to detect insider threats
    - Analyze network traffic for command & control communications
    - Investigate phishing campaigns and malware propagation
    
    Specialized techniques:
    - Time-series analysis of authentication failures and account lockouts
    - Graph analysis of lateral movement patterns
    - Statistical analysis of network traffic baselines
    - Threat intelligence correlation with IOCs and TTPs
    
    Provide security-specific outputs: STIX/TAXII format, risk scores, and IOC lists.
""")
```

### Financial Analysis Agent
```python
# Advanced financial modeling and analysis
response = client.add_cell(thread.id, """
    Act as a financial analysis specialist:
    
    Perform sophisticated financial analysis including:
    - Monte Carlo simulations for revenue forecasting
    - Cohort analysis for subscription revenue prediction
    - Unit economics modeling with sensitivity analysis
    - Cash flow projections under multiple scenarios
    - Competitive benchmarking and market analysis
    
    Advanced financial techniques:
    - Discounted cash flow valuations with WACC calculations
    - Financial ratio analysis with peer comparisons
    - Working capital optimization analysis
    - Capital allocation efficiency assessment
    
    Provide executive-ready financial models with assumptions documentation.
""")
```

### Marketing Attribution Agent
```python
# Advanced marketing attribution and optimization
response = client.add_cell(thread.id, """
    Act as a marketing attribution and optimization specialist:
    
    Perform sophisticated marketing analysis:
    - Multi-touch attribution modeling (linear, time-decay, position-based)
    - Marketing mix modeling (MMM) for channel effectiveness
    - Customer journey analysis across touchpoints
    - Incrementality testing and uplift measurement
    - Creative performance analysis with A/B testing
    
    Advanced marketing techniques:
    - Bayesian attribution modeling with uncertainty quantification
    - Media saturation curves and diminishing returns analysis
    - Cross-channel interaction effects and synergies
    - Lifetime value optimization across acquisition channels
    
    Provide actionable budget reallocation recommendations with expected ROI.
""")
```

## Advanced Patterns

### Iterative Refinement
```python
# Start broad, then narrow
response = client.add_cell(thread.id, "Show me sales trends")

# Refine based on initial results
response = client.add_cell(thread.id, 
    "Focus on the electronics category and break down by subcategory"
)

# Drill deeper
response = client.add_cell(thread.id,
    "For the top 3 subcategories, show customer demographics and buying patterns"
)
```

### Conditional Analysis
```python
# Dynamic analysis based on conditions
response = client.add_cell(thread.id, """
    Analyze customer churn:
    - If churn rate > 10%, deep dive into root causes
    - If specific segment shows high churn, analyze their journey
    - If seasonal pattern detected, compare with previous years
    - Generate retention strategies based on findings
""")
```

### Automated Reporting
```python
# Complete report generation
response = client.add_cell(thread.id, """
    Generate a weekly business intelligence report:
    1. Query all KPIs from various databases
    2. Calculate week-over-week changes
    3. Create visualizations for top metrics
    4. Identify and explain significant changes
    5. Generate executive summary
    6. Format as markdown with embedded charts
""")

# Save complete report
with open("weekly_report.md", "w") as f:
    f.write(response.content)
```

### Natural Language Data Exploration
```python
# Conversational analysis
response = client.add_cell(thread.id, 
    "What interesting patterns can you find in our customer data?"
)

# Follow up based on findings
response = client.add_cell(thread.id,
    "Tell me more about the seasonal pattern you mentioned"
)

# Get specific
response = client.add_cell(thread.id,
    "Which products drive this seasonality and what marketing strategies could we use?"
)
```

## Best Practices

### 1. Be Specific About Output Format
```python
# Good: Clear format specification
response = client.add_cell(thread.id, """
    Query sales data and:
    - Return as a DataFrame with columns: date, region, product, revenue
    - Sort by revenue descending
    - Include only top 100 results
""")

# Less effective: Vague request
response = client.add_cell(thread.id, "Show me sales data")
```

### 2. Combine Multiple Operations
```python
# Efficient: One query, multiple operations
response = client.add_cell(thread.id, """
    1. Query customer database for high-value customers
    2. Calculate their lifetime value
    3. Create a UMAP clustering visualization
    4. Generate insights about each cluster
""")

# Less efficient: Multiple separate queries
```

### 3. Use Context from Previous Queries
```python
# Build on previous results
df = response1.to_dataframe()
customer_ids = df['customer_id'].tolist()

response2 = client.add_cell(thread.id, 
    f"For customers {customer_ids}, analyze their purchase patterns and predict churn risk"
)
```

### 4. Request Explanations
```python
# Get insights with your data
response = client.add_cell(thread.id, """
    Query sales anomalies and explain:
    - Why each anomaly is significant
    - Potential business impact
    - Recommended actions
""")
```

## Quick Reference

| Goal | Query Pattern |
|------|---------------|
| Get data | "Query [database] for [data] where [conditions]" |
| Create visualization | "Create a [type] visualization showing [data] with [attributes]" |
| Analyze patterns | "Use TableAI to find [patterns] in [data] and explain [why]" |
| Generate insights | "Analyze [data] and provide insights about [topic]" |
| Multi-step workflow | "1. Query... 2. Then analyze... 3. Finally visualize..." |
| Cross-database | "Combine data from [db1] and [db2] to show [unified view]" |

## Next Steps

- Try these patterns with your own data
- Combine patterns for complex workflows  
- Share successful patterns with the community
- See [Response Types](../api/response-types.md) for handling different outputs