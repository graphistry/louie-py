# LouieAI Python Client

Welcome to the **LouieAI** Python client library documentation.

**LouieAI** is Graphistry's genAI-native investigation platform. This library allows Python applications to interact with LouieAI via its API, leveraging Graphistry authentication.

<video width="100%" controls autoplay muted loop>
  <source src="https://github.com/user-attachments/assets/de73f7b3-2862-4298-b9d8-2d38426ab255" type="video/mp4">
  Your browser does not support the video tag.
</video>

[Video: Louie <> Graphistry - Python edition!](https://www.loom.com/share/8d84c9abc0e34df6b233bd7b2e10af9a?sid=4a87707a-79e6-416b-a628-01b5c31c7db3)

## Install & Go

```bash
pip install louieai
```

```python
import graphistry
import louieai

# Configure servers and authenticate
graphistry.register(
    api=3, 
    server="hub.graphistry.com",  # Your Graphistry server
    username="alice@example.com", 
    password="<your_password>"
)

# Create Louie interface with server configuration
lui = louieai(server_url="https://den.louie.ai")  # Your Louie server

# Start analyzing
lui("Show me patterns in customer behavior")
print(lui.text)  # Natural language insights
df = lui.df      # Data as pandas DataFrame
```

## Powerful Options

```python
# Choose your authentication method
import louieai

# Option 1: Environment variables (great for notebooks)
# export GRAPHISTRY_USERNAME="your_username" 
# export GRAPHISTRY_PASSWORD="your_password"
lui = louieai()  # Auto-detects credentials

# Option 2: Specific servers and organizations
g = graphistry.register(
    api=3,
    server="hub.graphistry.com",  # or "your-company.graphistry.com"
    username="your_username",
    password="your_password",
    org_name="your-org"  # Optional: specify organization
)
lui = louieai(g, server_url="https://den.louie.ai")  # or your enterprise URL

# Control data visibility
lui = louieai(share_mode="Organization")  # Share within your org
lui("Analyze sales trends", share_mode="Private")  # Override per query

# Enable AI reasoning traces
lui.traces = True
lui("Complex analysis requiring step-by-step reasoning")

# Access conversation history
previous_result = lui[-1]  # Last response
older_df = lui[-2].df      # DataFrame from 2 queries ago
```

**Need more options?** See our guides:

- [Authentication Guide](guides/authentication.md) - All authentication methods including API keys, multi-tenant usage
- [Getting Started](getting-started/quick-start.md) - Complete walkthrough with examples
- [Agent Selection](guides/agent-selection.md) - Use specialized agents for databases and visualizations

## Key Features

- **Notebook-friendly API**: Streamlined `lui()` interface for Jupyter notebooks
- **Thread-based conversations**: Maintain context across multiple queries
- **Multiple response types**: Handle text, DataFrames, visualizations, and more
- **40+ Specialized Agents**: Choose from database-specific, visualization, and analysis agents
- **Real-time streaming**: See responses as they're generated in Jupyter notebooks
- **Natural language interface**: Access all Louie capabilities through simple prompts
- **Auto-refresh authentication**: Automatically handles JWT token expiration
- **Multiple auth methods**: Works with existing Graphistry sessions or direct credentials

### Available Agents with Semantic Understanding

LouieAI provides specialized agents that learn and understand your data:

- General Purpose: LouieAgent (default), TextAgent, CodeAgent
- Databases with Semantic Layer: DatabricksAgent, PostgresAgent, MySQLAgent, SnowflakeAgent, BigQueryAgent
  - Agents learn your schema, relationships, and business context
  - Generate complex queries from natural language using semantic understanding
- Search & Analytics: SplunkAgent, OpenSearchAgent, KustoAgent
- Visualizations: GraphAgent, PerspectiveAgent, KeplerAgent, MermaidAgent
- Direct Execution: PassthroughAgent variants for each database (no AI interpretation)

```python
# Use the default conversational agent
lui("Analyze security incidents from last week")

# Database agent with semantic understanding
lui("Show me customer churn trends", agent="DatabricksAgent")
# The agent understands your schema and business definitions of "churn"

# Natural language leveraging learned semantics
lui("Which products have anomalous return rates?", agent="PostgresAgent") 
# Agent knows your product hierarchy, return policies, and what's "anomalous"

# Direct SQL when you need exact control
lui("SELECT * FROM auth_logs WHERE status='failed'", agent="PostgresPassthroughAgent")
```

See the complete [Agents Reference](reference/agents.md) for all available agents and usage examples.

## Getting Started

New to LouieAI? Start here:

1. **[Installation](getting-started/installation.md)** - Install the LouieAI Python client
2. **[Authentication](getting-started/authentication.md)** - Set up authentication with PyGraphistry
3. **[Quick Start](getting-started/quick-start.md)** - Make your first queries and explore features

## User Guides

Ready to dive deeper? These guides cover common use cases and advanced features:

- **[Examples](guides/examples.md)** - Practical examples for both notebook and client APIs
- **[Query Patterns](guides/query-patterns.md)** - Advanced query techniques and best practices
- **[Authentication Guide](guides/authentication.md)** - Multi-tenant usage, API keys, and troubleshooting
- **[Agent Selection](guides/agent-selection.md)** - How to choose and use different agents
- **[Interactive Notebooks](getting-started/notebooks/01-getting-started.ipynb)** - Hands-on Jupyter notebook examples

## API Reference

Complete technical documentation:

- **[API Overview](api/index.md)** - Overview of the LouieAI API
- **[LouieClient Reference](api/client.md)** - Complete LouieClient documentation
- **[Response Types](api/response-types.md)** - Understanding LouieAI response formats
- **[Available Agents](reference/agents.md)** - Complete list of 40+ specialized agents

## Developer Resources

Contributing to LouieAI or setting up for development:

- **[Architecture](developer/architecture.md)** - How LouieAI and Graphistry integrate
- **[Development Guide](developer/development.md)** - Local development setup
- **[Testing](developer/testing.md)** - Running and writing tests
- **[Publishing](developer/publishing.md)** - Release process documentation

## Support

- **[GitHub Issues](https://github.com/graphistry/louie-py/issues)** - Report bugs or request features
- **[Graphistry Community](https://github.com/graphistry/pygraphistry)** - PyGraphistry support and community