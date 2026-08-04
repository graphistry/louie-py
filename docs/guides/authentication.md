# Authentication Guide

This guide covers all authentication options for LouieAI, from basic setup to advanced multi-tenant configurations.

## Overview

LouieAI uses PyGraphistry authentication - no separate credentials needed. Servers must be paired:

| Graphistry Server | Louie Server (`server_url`) | Usage |
|------------------|--------------|-------|
| `hub.graphistry.com` | `https://den.louie.ai` | Louie Web — public cloud (free tier) |
| `your-company.graphistry.com` | `https://louie.your-company.com` | Louie Web — enterprise deployment |
| whatever the desktop app is paired with | `http://127.0.0.1:10013` | Louie Desktop — app running on your machine |

LouieAI automatically extracts JWT tokens from PyGraphistry and refreshes them as needed.
Use `server_url` for the Louie API base and `graphistry_server` for Graphistry auth.

**Web vs Desktop:** `server_url` defaults to `https://den.louie.ai`, so web users can
usually omit it. Louie Desktop listens on `http://127.0.0.1:10013` and must always be set
explicitly — see [Connecting: Web vs Desktop](../getting-started/connecting.md).

**Resources:**
- [PyGraphistry Authentication](https://pygraphistry.readthedocs.io/en/latest/server/register.html) - All authentication methods
- [PyGraphistry Concurrency](https://pygraphistry.readthedocs.io/en/latest/server/concurrency.html) - Multi-tenant patterns

## Basic Authentication

### Method 1: Using Existing PyGraphistry Authentication

```python
import graphistry
import louieai

# For Graphistry Hub (free tier)
g = graphistry.register(
    api=3, 
    server="hub.graphistry.com",
    username="your_user", 
    password="your_pass"
)
lui = louieai(g, server_url="https://den.louie.ai")

# For Enterprise deployments
g = graphistry.register(
    api=3,
    server="your-company.graphistry.com",
    username="your_user",
    password="your_pass"
)
lui = louieai(g, server_url="https://louie.your-company.com")
```

### Method 2: Direct Credentials

```python
# Uses default servers (hub.graphistry.com + den.louie.ai)
lui = louieai(
    username="your_user",
    password="your_pass"
)

# Or specify custom servers
lui = louieai(
    username="your_user",
    password="your_pass",
    graphistry_server="your-company.graphistry.com",
    server_url="https://louie.your-company.com"
)
```

### Method 3: Using the Register Method

```python
from louieai import louie

# Create client with credentials
lui = louie(
    username="your_user",
    password="your_pass"
)
```

### Method 4: Using PyGraphistry Client Objects

```python
# Create an isolated PyGraphistry client
g = graphistry.client()
g.register(api=3, username="your_user", password="your_pass")

# Pass it to LouieAI
client = lui.LouieClient(graphistry_client=g)
```

### Method 5: API Key Authentication

```python
# Using legacy API key
client = lui.LouieClient(
    api_key="<your-api-key>",
    graphistry_server="hub.graphistry.com"
)

# Using personal key (service accounts)
client = lui.LouieClient(
    personal_key_id="pk_123...",
    personal_key_secret="sk_123...",
    org_name="my-org",  # Optional
    graphistry_server="hub.graphistry.com"
)
```

### Method 6: Environment Variables

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

### Method 7: Anonymous Desktop Authentication (Optional)

Louie Desktop can expose `/auth/anonymous` for local sessions with no Graphistry login.
This is a desktop-only feature and may be disabled; if so, the client raises a clear
error and you should authenticate with the credentials your desktop app is paired with.

```python
from louieai import louie

# Louie Desktop's local port — it proxies /api and hosts /auth/anonymous
lui = louie(
    server_url="http://127.0.0.1:10013",
    anonymous=True
)
```

Anonymous auth cannot be combined with Graphistry credentials.

If you already fetched a bearer token (Graphistry or anonymous), you can pass it
directly:

```python
from louieai import louie

lui = louie(
    server_url="http://127.0.0.1:10013",
    anonymous=True,
    token="<anon-token>"
)
```

## Multi-tenant Authentication

### Isolated Client Instances

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

**Key benefits:**
- Thread-safe concurrent usage
- Session isolation 
- Multi-server support

## Authentication Options Reference

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `username` | str | PyGraphistry username | `"alice"` |
| `password` | str | PyGraphistry password | `"secure_pass"` |
| `api_key` | str | API key (alternative to username/password) | `"api_key_123..."` |
| `personal_key_id` | str | Personal key ID for service accounts | `"pk_123..."` |
| `personal_key_secret` | str | Personal key secret for service accounts | `"sk_123..."` |
| `org_name` | str | Organization name (optional) | `"my-org"` |
| `graphistry_server` | str | Graphistry server URL | `"hub.graphistry.com"` |
| `api` | int | API version (usually 3) | `3` |
| `graphistry_client` | Any | Existing PyGraphistry client or plottable | `graphistry.client()` |
| `server_url` | str | Louie API base — web URL or Desktop's `http://127.0.0.1:10013` | `"https://den.louie.ai"` |
| `anonymous` | bool | Use `/auth/anonymous` (Louie Desktop only, optional) | `True` |
| `token` | str | Pre-fetched bearer token (anonymous or Graphistry) | `"<token>"` |
| `anonymous_timeout` | int | Timeout for `/auth/anonymous` request (seconds) | `20` |

## Security Best Practices

- Never hardcode credentials - use environment variables
- Use isolated clients for multi-tenant applications  
- Use personal keys for service accounts
- Regularly rotate credentials in production

## Additional Resources

- [LouieAI API Reference](../api/client.md) - Complete API documentation for LouieClient
