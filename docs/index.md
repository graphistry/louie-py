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

# Ask questions in natural language
lui("Show me users with unusual ordering patterns or velocity")

# Get behavioral fraud analysis instantly
print(lui.text)
# Output: "Identified 34 accounts with suspicious ordering behavior:
# 
# **High Velocity Orders**:
# • user_78234: 47 orders in 2 hours (avg basket: $67)
# • user_45891: 23 orders from same IP, different payment methods
# 
# **Geographic Inconsistencies**:
# • 12 accounts: Billing in NYC, shipping to warehouse addresses in TX
# • 8 accounts: VPN usage combined with expedited shipping
# 
# **Pattern Analysis**: 73% likely reseller activity, 18% promotional abuse"

# Access transaction patterns
patterns_df = lui.df
if patterns_df is not None:
    print("\nSuspicious ordering patterns:")
    print(patterns_df.head())
    #     user_id  orders_24h  avg_basket  billing_state shipping_state  pattern_type
    # 0  user_78234          47       $67         NY             TX      high_velocity
    # 1  user_45891          23      $134         CA             CA      payment_cycling  
    # 2  user_23456          18       $89         FL             WA      geo_inconsistent
```

## Key Features

- **Notebook-friendly API**: Streamlined `lui()` interface for Jupyter notebooks
- **Thread-based conversations**: Maintain context across multiple queries
- **Multiple response types**: Handle text, DataFrames, visualizations, and more
- **Streaming support**: Responses stream in real-time via JSONL
- **Natural language interface**: Access all Louie capabilities through simple prompts
- **Auto-refresh authentication**: Automatically handles JWT token expiration
- **Multiple auth methods**: Works with existing Graphistry sessions or direct credentials

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
- **[Interactive Notebooks](getting-started/notebooks/)** - Hands-on Jupyter notebook examples

## API Reference

Complete technical documentation:

- **[API Overview](api/index.md)** - Overview of the LouieAI API
- **[LouieClient Reference](api/client.md)** - Complete LouieClient documentation
- **[Response Types](api/response-types.md)** - Understanding LouieAI response formats

## Developer Resources

Contributing to LouieAI or setting up for development:

- **[Architecture](developer/architecture.md)** - How LouieAI and Graphistry integrate
- **[Development Guide](developer/development.md)** - Local development setup
- **[Testing](developer/testing.md)** - Running and writing tests
- **[Publishing](developer/publishing.md)** - Release process documentation

## Support

- **[GitHub Issues](https://github.com/graphistry/louie-py/issues)** - Report bugs or request features
- **[Graphistry Community](https://github.com/graphistry/pygraphistry)** - PyGraphistry support and community