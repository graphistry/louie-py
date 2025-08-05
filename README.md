# LouieAI Python Client

[![CI](https://github.com/graphistry/louie-py/actions/workflows/ci.yml/badge.svg)](https://github.com/graphistry/louie-py/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/louieai.svg)](https://pypi.org/project/louieai/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

AI-powered investigation platform for natural language data analysis.



https://github.com/user-attachments/assets/de73f7b3-2862-4298-b9d8-2d38426ab255

[Video: Louie <> Graphistry - Python edition!](https://www.loom.com/share/8d84c9abc0e34df6b233bd7b2e10af9a?sid=4a87707a-79e6-416b-a628-01b5c31c7db3)



## 🚀 Get Started in 30 Seconds

```python
# 1. Install
# pip install louieai

# 2. Authenticate with your PyGraphistry server
import graphistry
graphistry.register(
    api=3,
    server="hub.graphistry.com",  # or your enterprise server
    username="bob@company.com",   # your actual username
    password="<your-password>"    # your actual password
)

# 3. Start analyzing with natural language
from louieai.notebook import lui
lui("Show me all suspicious transactions from the last week")

# 4. Access the results
print(lui.text)  # Natural language explanation
df = lui.df      # Pandas DataFrame with the data
```

## Install & Authenticate

```bash
pip install louieai
```

### Authentication

LouieAI uses PyGraphistry for authentication. You'll need a free account:

1. **Get PyGraphistry credentials** at [hub.graphistry.com](https://hub.graphistry.com) (free signup)
2. **Set environment variables** or authenticate in code:

```bash
# Option 1: Environment variables (recommended for notebooks/scripts)
export GRAPHISTRY_USERNAME="sarah@analytics.com"
export GRAPHISTRY_PASSWORD="Analytics2024!"
export GRAPHISTRY_SERVER="hub.graphistry.com"  # or "my-company.graphistry.com"

# Optional: Custom Louie endpoint (defaults to https://louie.ai)
export LOUIE_URL="https://louie-enterprise.company.com"
```

```python
# Option 2: Authenticate in code
import graphistry
graphistry.register(
    api=3, 
    server="hub.graphistry.com",  # or your enterprise server
    username="mike@investigations.org", 
    password="password123"  # example password
)

# Optional: Use custom Louie server
from louieai import LouieClient
client = LouieClient(
    server_url="https://louie.ai",  # Louie service endpoint (default)
    server="hub.graphistry.com"      # PyGraphistry server (default)
)
```

### Quick Start

```python
# First, authenticate with your PyGraphistry server
import graphistry
graphistry.register(
    api=3,
    server="hub.graphistry.com",  # or your private server
    username="alice@example.com",
    password="password123"  # example password
)

# Now import and use LouieAI (two options)

# Option 1: New clean import (recommended)
import louieai
lui = louieai()  # Automatically uses PyGraphistry auth

# Option 2: Traditional import
from louieai.notebook import lui

# Ask questions in natural language  
lui("Find accounts sharing payment methods or shipping addresses")

# Get fraud insights instantly
print(lui.text)
# Output: "Found 23 suspicious account clusters sharing payment/shipping details:
# 
# **Payment Card Sharing**:
# • Card ending 4789: Used by 8 different accounts in 3 days
# • Card ending 2156: 5 accounts, all created within same hour
# 
# **Address Clustering**:
# • 123 Oak St: 12 accounts using same shipping address
# • suspicious_email@temp.com: 7 accounts with similar email patterns
# 
# **Risk Assessment**: 67% likely promotional abuse, 23% payment fraud"

# Access the connection data
clusters_df = lui.df
if clusters_df is not None:
    print(clusters_df.head())
    #     account_id shared_payment shared_address  cluster_size  risk_score
    # 0   user_1234      card_4789    123_oak_st            12        7.2
    # 1   user_5678      card_4789    456_elm_ave            8        6.8  
    # 2   user_9012      card_2156    123_oak_st            5        8.1
```

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
