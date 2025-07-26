# LouieClient

The main client class for interacting with the Louie.ai service.

## API Documentation

::: louieai.LouieClient

## Usage Examples

### Basic Usage

```python
import louieai
import graphistry

# First authenticate with Graphistry
graphistry.register(api=3, username="your_user", password="your_pass")

# Create client with default server
client = louieai.LouieClient()

# Ask a question
response = client.ask("Analyze the network patterns in my dataset")
print(response)
```

### Custom Server URL

```python
# Use a different Louie.ai endpoint
client = louieai.LouieClient(server_url="https://custom.louie.ai")
```

### Error Handling

```python
try:
    response = client.ask("My question")
except RuntimeError as e:
    if "No Graphistry API token" in str(e):
        print("Please authenticate with graphistry.register() first")
    elif "API returned error" in str(e):
        print(f"Server error: {e}")
    elif "Failed to connect" in str(e):
        print(f"Network error: {e}")
```

## Common Issues

### Authentication Errors

If you see "No Graphistry API token found", ensure you've called `graphistry.register()` with valid credentials before creating the LouieClient.

### Network Errors

Network errors are wrapped in `RuntimeError` with descriptive messages. Check your internet connection and verify the server URL is accessible.

### API Errors

HTTP errors from the API include the status code and any error message from the server response.