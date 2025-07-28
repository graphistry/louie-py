"""Enhanced Louie client that matches the documented API."""

import json
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
        api: int = 3,
        server: str | None = None,
    ):
        """Initialize the Louie client.

        Args:
            server_url: Base URL for the Louie.ai service
            graphistry_client: Existing Graphistry client to use for auth
            username: Username for direct authentication
            password: Password for direct authentication
            api_key: API key for direct authentication
            api: API version (default: 3)
            server: Graphistry server URL for direct authentication

        Examples:
            # Use existing graphistry authentication
            client = LouieClient()

            # Pass credentials directly
            client = LouieClient(
                username="user",
                password="pass",
                server="hub.graphistry.com"
            )

            # Use existing graphistry client
            g = graphistry.nodes(df)
            client = LouieClient(graphistry_client=g)
        """
        self.server_url = server_url.rstrip("/")
        self._client = httpx.Client(timeout=60.0)

        # Set up authentication
        self._auth_manager = AuthManager(
            graphistry_client=graphistry_client,
            username=username,
            password=password,
            api_key=api_key,
            api=api,
            server=server,
        )

        # If credentials provided, authenticate immediately
        if any([username, password, api_key]):
            # Build kwargs for register, excluding None values
            register_kwargs: dict[str, Any] = {}
            if username is not None:
                register_kwargs["username"] = username
            if password is not None:
                register_kwargs["password"] = password
            if api_key is not None:
                register_kwargs["key"] = api_key  # graphistry uses 'key' parameter
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
        self, thread_id: str, prompt: str, agent: str = "LouieAgent"
    ) -> Response:
        """Add a cell (query) to a thread and get response.

        Args:
            thread_id: Thread ID to add to (empty string creates new thread)
            prompt: Natural language query
            agent: Agent to use (default: LouieAgent)

        Returns:
            Response object containing thread_id and all elements
        """
        headers = self._get_headers()

        # Build query parameters
        params: dict[str, str] = {
            "query": prompt,
            "agent": agent,
            "ignore_traces": "true",  # Convert bool to string for HTTP params
            "share_mode": "Private",
        }

        # Add thread ID if continuing existing thread
        if thread_id:
            params["dthread_id"] = thread_id

        # Make request
        response = self._client.post(
            f"{self.server_url}/api/chat/", headers=headers, params=params
        )
        response.raise_for_status()

        # Parse JSONL response
        result = self._parse_jsonl_response(response.text)

        # Get the thread ID
        actual_thread_id = result["dthread_id"]

        # Return Response with all elements
        return Response(thread_id=actual_thread_id, elements=result["elements"])

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
