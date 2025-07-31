# LouieAI Python Client

[![CI](https://github.com/graphistry/louie-py/actions/workflows/ci.yml/badge.svg)](https://github.com/graphistry/louie-py/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/louieai.svg)](https://pypi.org/project/louieai/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

**LouieAI** is an AI-driven investigative platform by [Graphistry](https://www.graphistry.com) that brings generative AI into your data analysis workflows. This Python client library enables you to programmatically interact with Louie.ai using natural language queries.

## Features

- **Simple API**: Send natural language queries and receive structured responses
- **Seamless Authentication**: Integrates with PyGraphistry authentication
- **Rich Responses**: Get text answers, dataframes, and Graphistry visualizations
- **Thread-based Conversations**: Maintain context across multiple queries
- **Multi-tenant Safe**: Supports PyGraphistry client objects for isolated sessions
- **Type-safe**: Full type hints for better IDE support

*Alpha Release: Core functionality is available with more features coming soon.*

## Installation

Requires Python 3.10+ and an existing Graphistry account.

```bash
# Using uv (recommended)
uv pip install louieai

# Using pip
pip install louieai
```

## Quick Start

```python
import graphistry
import louieai as lui

# Authenticate with your Graphistry account (defaults to hub.graphistry.com)
graphistry.register(api=3, username="your_user", password="your_pass")

# Create a client and make queries (defaults to den.louie.ai)
client = lui.LouieClient()
response = client.add_cell("", "Show me patterns in the security logs")

# Access different response types
for text in response.text_elements:
    print(text['text'])
    
for df in response.dataframe_elements:
    print(df['table'])  # pandas DataFrame
```

### Server Configuration

**Graphistry Server** (defaults to `hub.graphistry.com`):
```python
# Use default Graphistry Hub
graphistry.register(api=3, username="your_user", password="your_pass")

# Or specify custom server
graphistry.register(api=3, server="your-server.graphistry.com", username="your_user", password="your_pass")
```

**Louie Server** (defaults to `den.louie.ai`):
```python
# Use default Louie API
client = lui.LouieClient()

# Or specify custom server
client = lui.LouieClient(server_url="https://your-custom-louie.ai")
```

See the [Authentication Guide](https://louie-py.readthedocs.io/en/latest/authentication/) for advanced options including multi-tenant usage, API keys, and concurrent sessions.

## Documentation

- [User Guide](https://louie-py.readthedocs.io) - Complete usage examples and tutorials
- [API Reference](https://louie-py.readthedocs.io/en/latest/api/) - Detailed API documentation
- [Examples](https://louie-py.readthedocs.io/en/latest/examples/) - Common patterns and use cases

## Links

- [Louie.ai Platform](https://louie.ai) - Learn about LouieAI
- [PyGraphistry](https://github.com/graphistry/pygraphistry) - Required for authentication
- [Support](https://github.com/graphistry/louie-py/issues) - Report issues or get help

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**For developers**: Check out [DEVELOP.md](DEVELOP.md) for technical setup and development workflow.

## License

Apache 2.0 - see [LICENSE](LICENSE)