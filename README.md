# LouieAI Python Client

[![CI](https://github.com/graphistry/louie-py/actions/workflows/ci.yml/badge.svg)](https://github.com/graphistry/louie-py/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/louieai.svg)](https://pypi.org/project/louieai/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

AI-powered investigation platform for natural language data analysis.

## Install & Go

```bash
pip install louieai
```

```python
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