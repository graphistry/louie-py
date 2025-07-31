# Architecture Overview

The **LouieAI client library** is designed to be lightweight and reliable. It primarily wraps calls to the LouieAI REST API with comprehensive error handling and clear feedback.

## Under the Hood

When you call `LouieClient.ask(prompt)`, the library:

1. **Fetches Authentication**: Retrieves your Graphistry authentication token (JWT) via `graphistry.api_token()`.
2. **Makes HTTP Request**: Issues an HTTP POST request to Louie.ai's REST API (default `https://den.louie.ai/api/ask`) with your prompt.
3. **Handles Authorization**: Includes the auth token in request headers (`Authorization: Bearer <token>`).
4. **Processes Response**: On success, returns the response parsed from JSON. This could be a direct answer (text or data) or instructions/results (e.g., a link to a Graphistry visualization or a summarized dataset).
5. **Provides Detailed Errors**: On failure, raises detailed `RuntimeError` exceptions:
   - **HTTP errors (4xx/5xx)**: Extracts JSON error messages from API response
   - **Network errors**: Provides network-specific error details  
   - **Missing authentication**: Clear message about calling graphistry.register()

## Design Principles

- **Stateless**: The client itself does not maintain any session state. Each call is independent (Louie.ai may maintain context on the server side).
- **Thread Safe**: Since we use no global state except Graphistry's global token, the client is lightweight. Instances can be created as needed.
- **Error Transparency**: All errors provide detailed information to help with debugging and troubleshooting.

## Response Types

LouieAI responses may include:
- **Text answers**: Direct responses to questions
- **JSON data**: Structured data results  
- **Graphistry visualization links**: References to generated graph visualizations
- **Database query results**: Summarized or processed data from connected sources

## Current Limitations

- **API Endpoint**: Uses `/api/ask` based on common REST patterns, subject to confirmation when official docs are available
- **Synchronous Only**: Currently supports synchronous requests only
- **Raw JSON**: Returns unprocessed JSON responses for maximum flexibility

## Future Enhancements

- **Streaming Responses**: For large responses or conversational use, streaming output (and an async API) might be added.
- **Result Handling**: In the future, the client could parse known response formats (like recognizing if a response contains a Graphistry visualization link) and provide helper methods.
- **Additional API Endpoints**: As Louie.ai grows (dashboards, agent management, etc.), this library will add corresponding methods.