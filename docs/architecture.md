# Architecture Overview

The **LouieAI client library** is designed to be lightweight. It primarily wraps calls to the LouieAI REST API.

- It uses the [PyGraphistry](https://github.com/graphistry/pygraphistry) library for authentication. You must login to Graphistry (cloud or on-prem) using `graphistry.register()` before using LouieAI functions.
- The core class `LouieClient` handles communication with LouieAI. It takes your prompt or query and sends it to the LouieAI service at `den.louie.ai`, using your Graphistry auth token for authorization.
- Responses are returned as Python data structures (parsed from JSON). In future versions, the client may support additional features like streaming responses or advanced query parameters.

**Note:** LouieAI is an evolving platform. This client is in early development (Alpha) and currently provides a basic interface for prompts. Future enhancements will include more robust error handling, support for different endpoints (dashboards, agents, etc.), and asynchronous call support.