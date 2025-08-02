# LouieAI Python Client

Welcome to the **LouieAI** Python client library documentation.

**LouieAI** is Graphistry's genAI-native investigation platform. This library allows Python applications to interact with LouieAI via its API, leveraging Graphistry authentication.

## Install & Go

```bash
pip install louieai
```

```python
# First, set up authentication with PyGraphistry
import graphistry

# Option 1: Environment variables (recommended for notebooks)
# In your terminal or notebook:
# export GRAPHISTRY_USERNAME="your_username"
# export GRAPHISTRY_PASSWORD="your_password"

# Then in Python:
import louieai
lui = louieai()  # Automatically uses the environment variables

# Option 2: Direct authentication
g = graphistry.register(
    api=3, 
    server="hub.graphistry.com",  # Graphistry Hub (free tier)
    username="your_username", 
    password="your_password"
)

# Now import and use LouieAI with the authenticated client
import louieai
lui = louieai(g, server_url="https://den.louie.ai")  # Specify Louie server

# Option 3: With organization and workspace settings
# For personal organization (most common):
g = graphistry.register(
    api=3,
    server="hub.graphistry.com",
    username="john_doe",
    password="your_password",
    org_name="john_doe"  # Personal orgs use your username
)
lui = louieai(g, server_url="https://den.louie.ai")

# For team organization:
g = graphistry.register(
    api=3,
    server="hub.graphistry.com",
    username="your_username",
    password="your_password",
    org_name="databricks-PAT-botsv3"  # Team organization name
)
lui = louieai(g, server_url="https://den.louie.ai")

# Control visibility of your threads
# Option A: Set default for the session
lui_private = louieai(g, server_url="https://den.louie.ai", share_mode="Private")
lui_org = louieai(g, server_url="https://den.louie.ai", share_mode="Organization")

# Option B: Override per query
lui("analyze my data")  # Uses session default
lui("analyze my data", share_mode="Organization")  # Override for this query
lui("analyze my data", share_mode="Public")  # Override for this query

# Note: Organization names are converted to slugs (lowercase, special chars become hyphens)
# Examples: "John Doe" → "john-doe", "My_Team!" → "my-team"

# For enterprise users:
# g = graphistry.register(api=3, server="your-company.graphistry.com", 
#                        org_name="your-org", ...)
# lui = louieai(g, server_url="https://louie.your-company.com")

## Example 1: Minimal Usage
# Just ask questions and get answers
lui("What are the key patterns in this data?")
print(lui.text)  # "I found 3 key patterns: ..."

## Example 2: Full Features
# Configure session defaults
lui = louieai(g, server_url="https://den.louie.ai", share_mode="Organization")
lui.traces = True  # Show AI reasoning steps

# Ask complex questions
lui("Show me users with unusual ordering patterns or velocity")

# Access multiple result types
print(lui.text)     # Text explanation
fraud_df = lui.df   # Generated dataframe
all_dfs = lui.dfs   # All dataframes in response

# Continue the conversation (maintains context)
lui("Now show me geographic anomalies")
geo_df = lui.df

# Override settings per query
lui("Create a private analysis", share_mode="Private", traces=False)

# Access conversation history
previous = lui[-1]  # Previous response
print(previous.text)
older_df = lui[-2].df  # Dataframe from 2 queries ago

# Thread management
print(lui.thread_id)  # Current thread ID
print(lui.url)        # URL to view thread
```

## Key Features

- **Notebook-friendly API**: Streamlined `lui()` interface for Jupyter notebooks
- **Thread-based conversations**: Maintain context across multiple queries
- **Multiple response types**: Handle text, DataFrames, visualizations, and more
- **40+ Specialized Agents**: Choose from database-specific, visualization, and analysis agents
- **Streaming support**: Responses stream in real-time via JSONL
- **Natural language interface**: Access all Louie capabilities through simple prompts
- **Auto-refresh authentication**: Automatically handles JWT token expiration
- **Multiple auth methods**: Works with existing Graphistry sessions or direct credentials

### 🤖 Available Agents with Semantic Understanding

LouieAI provides specialized agents that learn and understand your data:

- **General Purpose**: LouieAgent (default), TextAgent, CodeAgent
- **Databases with Semantic Layer**: 
  - DatabricksAgent, PostgresAgent, MySQLAgent, SnowflakeAgent, BigQueryAgent
  - Agents learn your schema, relationships, and business context
  - Generate complex queries from natural language using semantic understanding
- **Search & Analytics**: SplunkAgent, OpenSearchAgent, KustoAgent
- **Visualizations**: GraphAgent, PerspectiveAgent, KeplerAgent, MermaidAgent
- **Direct Execution**: PassthroughAgent variants for each database (no AI interpretation)

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
- **[Interactive Notebooks](getting-started/notebooks/)** - Hands-on Jupyter notebook examples

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