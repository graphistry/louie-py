# Basic Authentication

This guide covers the simplest way to authenticate with LouieAI using PyGraphistry.

## Quick Setup

LouieAI integrates seamlessly with PyGraphistry's authentication system:

```python
import graphistry
import louieai

# Option 1: Using environment variables (recommended)
# Set these in your environment:
# export GRAPHISTRY_USERNAME="your_user"
# export GRAPHISTRY_PASSWORD="your_pass"
lui = louieai()  # Automatically uses environment variables

# Option 2: Direct authentication
g = graphistry.register(api=3, username="your_user", password="your_pass")
lui = louieai(g)  # Pass the authenticated graphistry client

# Option 3: Pass credentials directly
lui = louieai(username="your_user", password="your_pass")

# Now you can make queries with any method
response = lui("What insights can you find in my data?")
print(lui.text)
```

That's it! LouieAI will automatically use your PyGraphistry credentials.

## How It Works

When you authenticate with PyGraphistry:
1. PyGraphistry handles the authentication with your Graphistry server
2. LouieAI extracts the JWT token from PyGraphistry 
3. The token is used for all LouieAI API requests
4. Tokens are automatically refreshed when needed

## Advanced Authentication

For more advanced authentication scenarios including:
- API key authentication
- Multi-tenant usage with isolated clients
- Direct credential passing
- Multi-server configurations
- Error handling and troubleshooting

See the comprehensive [Authentication Guide](../guides/authentication.md).

## Next Steps

Once authenticated, try the [Quick Start Guide](quick-start.md) to make your first queries.