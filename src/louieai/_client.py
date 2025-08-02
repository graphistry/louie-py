"""Enhanced Louie client that matches the documented API."""

import json
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .auth import AuthManager, auto_retry_auth


@dataclass
class Thread:
    """Represents a Louie conversation thread."""

    id: str
    name: str | None = None


class Response:
    """Response containing thread_id and multiple elements from a query."""

    def __init__(self, thread_id: str, elements: list[dict[str, Any]]):
        """Initialize response with thread ID and elements.

        Args:
            thread_id: The thread ID this response belongs to
            elements: List of element dictionaries from the response
        """
        self.thread_id = thread_id
        self.elements = elements

    @property
    def text_elements(self) -> list[dict[str, Any]]:
        """Get all text elements from the response."""
        return [e for e in self.elements if e.get("type") == "TextElement"]

    @property
    def dataframe_elements(self) -> list[dict[str, Any]]:
        """Get all dataframe elements from the response."""
        return [e for e in self.elements if e.get("type") == "DfElement"]

    @property
    def graph_elements(self) -> list[dict[str, Any]]:
        """Get all graph elements from the response."""
        return [e for e in self.elements if e.get("type") == "GraphElement"]

    @property
    def has_dataframes(self) -> bool:
        """Check if response contains any dataframe elements."""
        return len(self.dataframe_elements) > 0

    @property
    def has_graphs(self) -> bool:
        """Check if response contains any graph elements."""
        return len(self.graph_elements) > 0

    @property
    def has_errors(self) -> bool:
        """Check if response contains any error elements."""
        return any(e.get("type") == "ExceptionElement" for e in self.elements)


class LouieClient:
    """
    Enhanced client for Louie.ai that matches the documented API.

    This client provides thread-based conversations with natural language queries.

    Authentication can be handled in multiple ways:
    1. Pass an existing Graphistry client
    2. Pass credentials directly
    3. Use existing graphistry.register() authentication
    """

    def __init__(
        self,
        server_url: str = "https://den.louie.ai",
        graphistry_client: Any | None = None,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        personal_key_id: str | None = None,
        personal_key_secret: str | None = None,
        org_name: str | None = None,
        api: int = 3,
        server: str | None = None,
        timeout: float = 300.0,  # 5 minutes default for agentic flows
        streaming_timeout: float = 120.0,  # 2 minutes for streaming chunks
    ):
        """Initialize the Louie client.

        Args:
            server_url: Base URL for the Louie.ai service
            graphistry_client: Existing Graphistry client to use for auth
            username: Username for direct authentication
            password: Password for direct authentication
            api_key: API key for direct authentication (legacy)
            personal_key_id: Personal key ID for service account authentication
            personal_key_secret: Personal key secret for service account authentication
            org_name: Organization name (optional for all auth methods)
            api: API version (default: 3)
            server: Graphistry server URL for direct authentication
            timeout: Overall timeout in seconds for requests (default: 300s/5min)
            streaming_timeout: Timeout for streaming chunks (default: 120s/2min)

        Examples:
            # Use existing graphistry authentication
            client = LouieClient()

            # Pass username/password credentials
            client = LouieClient(
                username="user",
                password="pass",
                server="hub.graphistry.com"
            )

            # Use personal key authentication (recommended for service accounts)
            client = LouieClient(
                personal_key_id="ZD5872XKNF",
                personal_key_secret="SA0JJ2DTVT6LLO2S",
                server="hub.graphistry.com"
            )

            # Specify organization
            client = LouieClient(
                username="user",
                password="pass",
                org_name="my-org",
                server="hub.graphistry.com"
            )

            # Use existing graphistry client
            g = graphistry.nodes(df)
            client = LouieClient(graphistry_client=g)
        """
        self.server_url = server_url.rstrip("/")
        self._timeout = timeout
        self._streaming_timeout = streaming_timeout
        self._client = httpx.Client(timeout=timeout)

        # Set up authentication
        self._auth_manager = AuthManager(
            graphistry_client=graphistry_client,
            username=username,
            password=password,
            api_key=api_key,
            personal_key_id=personal_key_id,
            personal_key_secret=personal_key_secret,
            org_name=org_name,
            api=api,
            server=server,
        )

        # If credentials provided, authenticate immediately
        if any([username, password, api_key, personal_key_id, personal_key_secret]):
            # Build kwargs for register, excluding None values
            register_kwargs: dict[str, Any] = {}
            if personal_key_id is not None and personal_key_secret is not None:
                # Use personal key authentication
                register_kwargs["personal_key_id"] = personal_key_id
                register_kwargs["personal_key_secret"] = personal_key_secret
            elif api_key is not None:
                # Use API key authentication
                register_kwargs["key"] = api_key  # graphistry uses 'key' parameter
            elif username is not None and password is not None:
                # Use username/password authentication
                register_kwargs["username"] = username
                register_kwargs["password"] = password

            # Add common parameters
            if org_name is not None:
                register_kwargs["org_name"] = org_name
            if api is not None:
                register_kwargs["api"] = api
            if server is not None:
                register_kwargs["server"] = server

            if register_kwargs:
                self.register(**register_kwargs)

    @property
    def auth_manager(self) -> AuthManager:
        """Get the authentication manager."""
        return self._auth_manager

    def register(self, **kwargs: Any) -> "LouieClient":
        """Register authentication credentials (passthrough to graphistry).

        Args:
            **kwargs: Same arguments as graphistry.register()

        Returns:
            Self for chaining

        Examples:
            client.register(username="user", password="pass")
            client.register(api_key="key-123")
        """
        self._auth_manager._graphistry_client.register(**kwargs)
        return self

    def _get_headers(self) -> dict[str, str]:
        """Get authorization headers using auth manager."""
        token = self._auth_manager.get_token()
        return {"Authorization": f"Bearer {token}"}

    def _parse_jsonl_response(self, response_text: str) -> dict[str, Any]:
        """Parse JSONL response into structured data.

        Returns dict with:
        - dthread_id: The thread ID
        - elements: List of response elements
        """
        result: dict[str, Any] = {"dthread_id": None, "elements": []}

        # Track elements by ID to handle streaming updates
        elements_by_id = {}

        for line in response_text.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)

                # First line contains thread ID
                if "dthread_id" in data:
                    result["dthread_id"] = data["dthread_id"]

                # Subsequent lines contain element updates
                elif "payload" in data:
                    elem = data["payload"]
                    elem_id = elem.get("id")
                    if elem_id:
                        # Update or add element
                        elements_by_id[elem_id] = elem

            except json.JSONDecodeError:
                continue

        # Convert to list, preserving order
        result["elements"] = list(elements_by_id.values())
        return result

    def create_thread(
        self, name: str | None = None, initial_prompt: str | None = None
    ) -> Thread:
        """Create a new conversation thread.

        Args:
            name: Optional name for the thread
            initial_prompt: Optional first message to initialize thread

        Returns:
            Thread object with ID

        Note: If no initial_prompt, thread ID will be empty until first add_cell
        """
        if initial_prompt:
            # Create thread with initial message
            response = self.add_cell("", initial_prompt)
            return Thread(id=response.thread_id, name=name)
        else:
            # Return placeholder - actual thread created on first add_cell
            return Thread(id="", name=name)

    @auto_retry_auth
    def add_cell(
        self,
        thread_id: str,
        prompt: str,
        agent: str = "LouieAgent",
        *,
        traces: bool = False,
    ) -> Response:
        """Add a cell (query) to a thread and get response.

        Args:
            thread_id: Thread ID to add to (empty string creates new thread)
            prompt: Natural language query
            agent: Agent to use (default: LouieAgent)
            traces: Whether to include reasoning traces in response (default: False)

        Returns:
            Response object containing thread_id and all elements
        """
        headers = self._get_headers()

        # Build query parameters
        params: dict[str, str] = {
            "query": prompt,
            "agent": agent,
            # Convert bool to string for HTTP params
            "ignore_traces": str(not traces).lower(),
            "share_mode": "Private",
        }

        # Add thread ID if continuing existing thread
        if thread_id:
            params["dthread_id"] = thread_id

        # Make streaming request with custom timeout handling
        response_text = ""
        lines_received = 0
        start_time = time.time()

        # Use configured timeouts
        with (
            httpx.Client(
                timeout=httpx.Timeout(
                    self._timeout,  # Overall timeout
                    read=self._streaming_timeout,  # Per-chunk timeout
                )
            ) as stream_client,
            stream_client.stream(
                "POST", f"{self.server_url}/api/chat/", headers=headers, params=params
            ) as response,
        ):
            response.raise_for_status()

            # Collect streaming lines
            try:
                for line in response.iter_lines():
                    if line:
                        response_text += line + "\n"
                        lines_received += 1

                        # Keep reading all elements until stream ends
                        # Don't break early just because we got a text element

                    # Safety timeout - use configured timeout
                    if time.time() - start_time > self._timeout:
                        break

            except httpx.ReadTimeout as e:
                elapsed = time.time() - start_time
                # This is expected - the server keeps the connection open
                # If we have at least 2 lines, that's a valid response
                if lines_received >= 2:
                    pass
                else:
                    raise RuntimeError(
                        f"Louie API timeout after {elapsed:.1f}s waiting for "
                        f"response. Only received {lines_received} lines. "
                        f"Agentic flows can take time - consider increasing "
                        f"timeout (current: {self._streaming_timeout}s per chunk, "
                        f"{self._timeout}s total). "
                        f"Set timeout parameter when creating LouieClient."
                    ) from e

        # Log if request took a long time
        total_time = time.time() - start_time
        if total_time > 30:
            import warnings

            warnings.warn(
                f"Louie API request took {total_time:.1f}s to complete. "
                f"This is normal for complex agentic flows, but if you're "
                f"seeing timeouts, consider increasing the timeout parameter "
                f"when creating LouieClient.",
                RuntimeWarning,
                stacklevel=2,
            )

        # Parse JSONL response
        result = self._parse_jsonl_response(response_text)

        # Get the thread ID
        actual_thread_id = result["dthread_id"]

        # Return Response with all elements
        return Response(thread_id=actual_thread_id, elements=result["elements"])

    def __call__(
        self,
        prompt: str,
        *,
        thread_id: str | None = None,
        traces: bool = False,
        agent: str = "LouieAgent",
        **kwargs: Any,
    ) -> Response:
        """Make the client callable for ergonomic usage.

        This allows using the client like a function:
        ```python
        client = LouieClient()
        response = client("What's the weather?")
        ```

        Args:
            prompt: Natural language query
            thread_id: Thread ID to use (None creates new thread)
            traces: Whether to include reasoning traces
            agent: Agent to use (default: LouieAgent)
            **kwargs: Additional arguments (reserved for future use)

        Returns:
            Response object containing thread_id and all elements
        """
        # Use empty string for new thread if thread_id is None
        tid = thread_id if thread_id is not None else ""

        # Store the thread_id for subsequent calls if not provided
        if not hasattr(self, "_current_thread_id"):
            self._current_thread_id = None

        # Use stored thread_id if none provided
        if thread_id is None and self._current_thread_id is not None:
            tid = self._current_thread_id

        # Make the call
        response = self.add_cell(
            thread_id=tid, prompt=prompt, agent=agent, traces=traces
        )

        # Store thread_id for next call
        if response.thread_id:
            self._current_thread_id = response.thread_id

        return response

    @auto_retry_auth
    def list_threads(self, page: int = 1, page_size: int = 20) -> list[Thread]:
        """List available threads.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            List of Thread objects
        """
        headers = self._get_headers()

        response = self._client.get(
            f"{self.server_url}/api/dthreads",
            headers=headers,
            params={
                "page": page,
                "page_size": page_size,
                "sort_by": "last_modified",
                "sort_order": "desc",
            },
        )
        response.raise_for_status()

        data = response.json()
        threads = []
        for item in data.get("items", []):
            threads.append(Thread(id=item.get("id", ""), name=item.get("name")))

        return threads

    @auto_retry_auth
    def get_thread(self, thread_id: str) -> Thread:
        """Get a specific thread by ID.

        Args:
            thread_id: Thread ID to retrieve

        Returns:
            Thread object
        """
        headers = self._get_headers()

        response = self._client.get(
            f"{self.server_url}/api/dthreads/{thread_id}", headers=headers
        )
        response.raise_for_status()

        data = response.json()
        return Thread(id=data.get("id", ""), name=data.get("name"))

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up client on exit."""
        self._client.close()
