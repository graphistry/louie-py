# LouieAI Python Client

Welcome to the **LouieAI** Python client library documentation.

**LouieAI** is Graphistry's genAI-native investigation platform. This library allows Python applications to interact with LouieAI via its API, leveraging Graphistry authentication.

## Installation

You can install the package via pip:
```bash
uv pip install louieai
```
(Note: The package may not be on PyPI yet if you're reading early.)

## Usage Example

```python
import graphistry
from louieai import LouieClient

# First, authenticate with Graphistry (replace with your credentials or key)
graphistry.register(api=3, username="your_user", password="your_pass")

client = LouieClient()
response = client.ask("What insights can you find about X dataset?")
print(response)
```

This will send the prompt to LouieAI and return a response (e.g., an answer or a visualization link).

See the [Architecture](architecture.md) page for more details on how LouieAI and Graphistry integrate.