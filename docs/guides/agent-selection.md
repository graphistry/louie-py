# Agent Selection Guide

LouieAI automatically selects the appropriate agents based on your query, but understanding the available agents helps you craft more effective queries.

## Agent Categories

### Database Agents
For querying structured data in various database systems:
- **Athena**: AWS Athena queries on S3 data
- **BigQuery**: Google BigQuery analytics
- **Snowflake**: Snowflake data warehouse queries
- **PostgreSQL/MySQL**: Traditional relational databases
- **Splunk**: Log analysis and security investigations

### Visualization Agents
For creating visual representations of your data:
- **Graph**: Network visualizations using Graphistry
- **Perspective**: Interactive data tables and charts
- **Kepler**: Geospatial mapping and analysis
- **Mermaid**: Flowcharts and diagrams

### Code & Development Agents
For executing code and creating notebooks:
- **Code**: Python code generation and execution
- **Notebook**: Jupyter notebook creation and modification

### Data Processing Agents
For specialized data operations:
- **TableAI**: Advanced table analysis and transformations
- **Firecrawl**: Web scraping and data extraction

## Automatic Selection

LouieAI uses several factors to select agents:

1. **Query Keywords**: Specific terms trigger relevant agents
   - "graph" or "network" → Graph agent
   - "map" or "geographic" → Kepler agent
   - "code" or "python" → Code agent

2. **Data Context**: The type of data influences agent selection
   - Graph data → Graph visualization
   - Tabular data → Perspective or TableAI
   - Log data → Splunk or appropriate database agent

3. **Task Type**: The requested operation determines agents
   - Analysis → Database + Code agents
   - Visualization → Appropriate viz agent
   - Investigation → Multiple coordinated agents

## Manual Agent Hints

While automatic selection usually works well, you can hint at specific agents:

```python
# Explicitly request graph visualization
lui("Show this data as a network graph")

# Request code generation
lui("Write Python code to analyze this dataset")

# Ask for geographic visualization
lui("Map these IP addresses to show geographic distribution")
```

## Multi-Agent Workflows

Complex queries often use multiple agents:

```python
# This might use: Database → Code → Graph agents
lui("Query user transactions from the database, calculate risk scores, and visualize the high-risk network")
```

## Performance Considerations

- **Database agents**: Best for large-scale data queries
- **Code agents**: Flexible but may be slower for simple operations
- **Visualization agents**: Require data to be loaded first

## Troubleshooting

If the wrong agent is selected:
1. Add more specific keywords to your query
2. Break complex queries into steps
3. Specify the desired output format

## See Also
- [Query Patterns](query-patterns.md) - Effective query strategies
- [Agent Guides](agents/index.md) - Detailed documentation for each agent
- [Examples](examples.md) - Real-world usage examples