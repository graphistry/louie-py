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
- **Type-safe**: Full type hints for better IDE support

*Alpha Release: Core functionality is available with more features coming soon.*

## Installation

Requires Python 3.12+ and an existing Graphistry account.

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

# Authenticate with your Graphistry account
graphistry.register(api=3, username="your_user", password="your_pass")

# Create a client and ask questions
client = lui.Client()
response = client.ask("Show me patterns in the security logs")

# Access different response types
for text in response.text_elements:
    print(text['text'])
    
for df in response.df_elements:
    print(df['table'])  # pandas DataFrame
```

## Documentation

- [User Guide](https://louieai.readthedocs.io) - Complete usage examples and tutorials
- [API Reference](https://louieai.readthedocs.io/en/latest/api/) - Detailed API documentation
- [Examples](https://louieai.readthedocs.io/en/latest/examples/) - Common patterns and use cases

## Links

- [Louie.ai Platform](https://louie.ai) - Learn about LouieAI
- [PyGraphistry](https://github.com/graphistry/pygraphistry) - Required for authentication
- [Support](https://github.com/graphistry/louie-py/issues) - Report issues or get help

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**For developers**: Check out [DEVELOP.md](DEVELOP.md) for technical setup and development workflow.

## License

Apache 2.0 - see [LICENSE](LICENSE)

The Apache-2.0 license enables easy integration in enterprise environments, Splunk apps, and Jupyter notebooks.