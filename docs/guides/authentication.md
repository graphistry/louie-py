# Authentication Guide

This guide covers all authentication options for LouieAI, from basic setup to advanced multi-tenant configurations.

## Overview

**LouieAI uses PyGraphistry for authentication** - you don't need separate credentials. When you authenticate with PyGraphistry, LouieAI automatically uses those credentials to connect to the Louie.ai service.

**Server Options:**
- **Use Graphistry Hub** - Free account at [hub.graphistry.com](https://hub.graphistry.com)
- **Run your own server** - Deploy PyGraphistry on your infrastructure

### How It Works

The authentication flow is simple:

1. **Authenticate with PyGraphistry** (via `graphistry.register()` or client objects)
2. **LouieAI extracts the JWT token** from PyGraphistry automatically
3. **Token is refreshed** when needed without user intervention

## Basic Authentication

### Method 1: Using Existing PyGraphistry Authentication

The simplest approach - authenticate once with PyGraphistry and LouieAI uses those credentials:

```python
import graphistry
import louieai as lui

# Authenticate with PyGraphistry
graphistry.register(api=3, username="your_user", password="your_pass")

# LouieAI automatically uses the PyGraphistry authentication
client = lui.LouieClient()
```

### Method 2: Direct Credentials

Pass credentials directly to LouieClient:

```python
client = lui.LouieClient(
    username="your_user",
    password="your_pass",
    server="hub.graphistry.com"  # Optional: specify server
)
```

### Method 3: Using the Register Method

Register after creating the client:

```python
client = lui.LouieClient()
client.register(
    username="your_user",
    password="your_pass",
    api=3
)
```

### Method 4: Using PyGraphistry Client Objects

For isolated authentication contexts:

```python
# Create an isolated PyGraphistry client
g = graphistry.client()
g.register(api=3, username="your_user", password="your_pass")

# Pass it to LouieAI
client = lui.LouieClient(graphistry_client=g)
```

### Method 5: API Key Authentication

Use PyGraphistry API keys for programmatic access:

```python
# Using legacy API key
client = lui.LouieClient(
    api_key="your_api_key",
    server="hub.graphistry.com"
)

# Using personal key (service accounts)
client = lui.LouieClient(
    personal_key_id="pk_123...",
    personal_key_secret="sk_123...",
    org_name="my-org",  # Optional
    server="hub.graphistry.com"
)
```

### Method 6: Environment Variables

Set authentication credentials via environment variables:

```bash
# Username/password authentication
export GRAPHISTRY_USERNAME=your_username
export GRAPHISTRY_PASSWORD=your_password

# API key authentication
export GRAPHISTRY_API_KEY=your_api_key

# Personal key authentication (service accounts)
export GRAPHISTRY_PERSONAL_KEY_ID=pk_123...
export GRAPHISTRY_PERSONAL_KEY_SECRET=sk_123...
export GRAPHISTRY_ORG_NAME=my-org  # Optional
```

Then use the notebook API or create a client without explicit credentials:

```python
# Notebook API automatically uses environment variables
from louieai.notebook import lui
lui("Your query here")

# Or with traditional client
import louieai as lui
client = lui.LouieClient()  # Uses env vars automatically
```

## Multi-tenant Authentication

For applications serving multiple users or requiring concurrent sessions with different credentials.

### Isolated Client Instances

Create separate LouieClient instances with distinct PyGraphistry clients to ensure complete isolation:

```python
import graphistry
import louieai as lui

# Create isolated client for Alice
alice_g = graphistry.client()
alice_g.register(api=3, username="alice", password="alice_pass")
alice_client = lui.LouieClient(graphistry_client=alice_g)

# Create isolated client for Bob
bob_g = graphistry.client()
bob_g.register(api=3, username="bob", password="bob_pass")
bob_client = lui.LouieClient(graphistry_client=bob_g)

# Each client operates independently
alice_response = alice_client.add_cell("", "Alice's secure query")
bob_response = bob_client.add_cell("", "Bob's secure query")

# No cross-contamination between sessions
print(f"Alice's thread: {alice_response.thread_id}")
print(f"Bob's thread: {bob_response.thread_id}")
```

### Multi-server Support

Connect different users to different Graphistry servers:

```python
# Production server for Alice
alice_g = graphistry.client()
alice_g.register(
    api=3, 
    server="prod.graphistry.com",
    username="alice",
    password="alice_pass"
)
alice_client = lui.LouieClient(graphistry_client=alice_g)

# Staging server for Bob
bob_g = graphistry.client()
bob_g.register(
    api=3,
    server="staging.graphistry.com", 
    username="bob",
    password="bob_pass"
)
bob_client = lui.LouieClient(graphistry_client=bob_g)
```

### Concurrent Usage Patterns

The isolated client pattern ensures:
- **No confused deputy issues**: Each client maintains its own authentication state
- **Thread safety**: Safe for concurrent use in web applications
- **Session isolation**: User sessions don't interfere with each other

Example in a web application:

```python
def handle_user_request(user_credentials):
    # Create isolated client for this user
    user_g = graphistry.client()
    user_g.register(api=3, **user_credentials)
    user_client = lui.LouieClient(graphistry_client=user_g)
    
    # Process user's request
    response = user_client.add_cell("", user_query)
    return response
```

## Authentication Options Reference

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `username` | str | PyGraphistry username | `"alice"` |
| `password` | str | PyGraphistry password | `"secure_pass"` |
| `api_key` | str | API key (alternative to username/password) | `"api_key_123..."` |
| `personal_key_id` | str | Personal key ID for service accounts | `"pk_123..."` |
| `personal_key_secret` | str | Personal key secret for service accounts | `"sk_123..."` |
| `org_name` | str | Organization name (optional) | `"my-org"` |
| `server` | str | Graphistry server URL | `"hub.graphistry.com"` |
| `api` | int | API version (usually 3) | `3` |
| `graphistry_client` | Any | Existing PyGraphistry client or plottable | `graphistry.client()` |

## Error Handling & Troubleshooting

### Common Authentication Errors

**401 Unauthorized**
```python
# JWT token expired - LouieAI automatically refreshes
# If refresh fails, check credentials
```

**Connection Errors**
```python
# Verify server URL and network connectivity
# Default server: hub.graphistry.com
```

### JWT Token Management

LouieAI automatically:
- Extracts JWT tokens from PyGraphistry
- Refreshes expired tokens
- Retries failed requests after token refresh

Manual token refresh (rarely needed):
```python
client.auth_manager.refresh_token()
```

## Security Best Practices

1. **Never hardcode credentials** - Use environment variables or secure vaults
2. **Use isolated clients** for multi-tenant applications
3. **Regularly rotate credentials** in production
4. **Monitor authentication logs** for suspicious activity

Example using environment variables:
```python
import os
import louieai as lui

client = lui.LouieClient(
    username=os.environ["GRAPHISTRY_USERNAME"],
    password=os.environ["GRAPHISTRY_PASSWORD"]
)
```

## Additional Resources

- [PyGraphistry Authentication Guide](https://pygraphistry.readthedocs.io/en/latest/server/register.html) - Comprehensive guide to PyGraphistry authentication options
- [PyGraphistry Concurrency Guide](https://pygraphistry.readthedocs.io/en/latest/server/concurrency.html) - Best practices for concurrent PyGraphistry usage
- [LouieAI API Reference](../api/client.md) - Complete API documentation for LouieClient