"""Mock objects and utilities for unit testing."""

import json
from typing import Any
from unittest.mock import Mock


class MockDataFrame:
    """Mock pandas DataFrame that behaves like real one for tests."""

    def __init__(self, data=None):
        if data is None:
            data = {
                "source_ip": ["192.168.1.1", "10.0.0.1", "172.16.0.1"],
                "user": ["alice", "bob", "charlie"],
                "value": [100, 200, 300],
                "customer_id": ["cust001", "cust002", "cust003"],
            }
        self._data = data

    def __getitem__(self, key):
        if key in self._data:
            return MockSeries(self._data[key])
        return self

    def unique(self):
        """Return unique values."""

        # Return an array-like object with tolist method
        class ArrayLike(list):
            def tolist(self):
                return list(self)

        return ArrayLike(["192.168.1.1", "10.0.0.1", "172.16.0.1"])

    def tolist(self):
        """Convert to list."""
        # Return the data for the first column
        first_col = next(iter(self._data.values())) if self._data else []
        return first_col

    def describe(self):
        """Return description."""
        return f"Mock DataFrame with {len(self._data.get('user', []))} rows"

    def __len__(self):
        return len(next(iter(self._data.values()))) if self._data else 0


class MockSeries:
    """Mock pandas Series."""

    def __init__(self, data):
        self._data = data

    def unique(self):
        # Return a numpy-like array that has tolist() method
        class ArrayLike(list):
            def tolist(self):
                return list(self)

        return ArrayLike(list(set(self._data)))

    def tolist(self):
        return list(self._data)


class MockResponse:
    """Mock response object for Louie API."""

    def __init__(self, response_type: str = "text", thread_id: str = "D_test001"):
        self.thread_id = thread_id
        self.type = self._get_type_name(response_type)
        self.id = f"B_{response_type}_{id(self)}"
        self._setup_response_data(response_type)

    def _get_type_name(self, response_type: str) -> str:
        """Get proper element type name."""
        type_map = {
            "text": "TextElement",
            "dataframe": "DfElement",
            "graph": "GraphElement",
            "exception": "ExceptionElement",
            "image": "Base64ImageElement",
        }
        return type_map.get(response_type, "TextElement")

    def _setup_response_data(self, response_type: str):
        """Set up response data based on type."""
        if response_type == "dataframe":
            self.to_dataframe = Mock(return_value=MockDataFrame())
            self.metadata = {
                "shape": [100, 5],
                "columns": ["id", "name", "value", "created_at", "status"],
            }
            # Also set text for dataframe responses
            self.text = "Here is the data you requested"
            self.content = self.text
        elif response_type == "graph":
            self.dataset_id = "abc123def456"
            self.status = "completed"
            self.text = "Graph visualization created"
            self.content = self.text
        elif response_type == "exception":
            self.error_type = "ValidationError"
            self.message = "Test error message"
            self.traceback = "Traceback (most recent call last)..."
            self.text = "Error: Test error message"
            self.content = self.text
        elif response_type == "image":
            self.src = "data:image/png;base64,iVBORw0KGgoAAAANS..."
            self.alt = "Generated chart"
            self.text = "Image generated"
            self.content = self.text
        else:  # text
            self.text = "Sample analysis response with insights"
            self.content = self.text  # Alias
            self.language = "Markdown"

        # Add elements list and convenience properties
        self._setup_elements(response_type)

        # Ensure text_elements is always populated for text responses
        if response_type == "text" and not self.text_elements:
            # Force add a text element
            self.elements.append(
                {
                    "type": "TextElement",
                    "id": self.id,
                    "content": self.text,
                    "language": "Markdown",
                }
            )

    def _setup_elements(self, response_type: str):
        """Set up elements list and convenience properties."""
        # Create elements list based on response type
        element = {
            "type": self.type,
            "id": self.id,
        }

        if response_type == "text":
            element.update(
                {
                    "content": self.text,
                    "language": getattr(self, "language", "Markdown"),
                }
            )
        elif response_type == "dataframe":
            element.update({"metadata": self.metadata, "table": MockDataFrame()})
        elif response_type == "graph":
            element.update({"dataset_id": self.dataset_id, "status": self.status})
        elif response_type == "exception":
            element.update(
                {
                    "error_type": self.error_type,
                    "message": self.message,
                    "traceback": self.traceback,
                }
            )
        elif response_type == "image":
            element.update({"src": self.src, "alt": self.alt})

        self.elements = [element]

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
    def has_graphs(self) -> bool:
        """Check if response has graph elements."""
        return len(self.graph_elements) > 0

    @property
    def has_dataframes(self) -> bool:
        """Check if response has dataframe elements."""
        return len(self.dataframe_elements) > 0

    @property
    def has_errors(self) -> bool:
        """Check if response has error elements."""
        return any(e.get("type") == "ExceptionElement" for e in self.elements)

    def to_dataframe(self):
        """Return mock dataframe (for backward compatibility)."""
        if self.type == "DfElement":
            return MockDataFrame()
        return None


class MockThread:
    """Mock thread object."""

    def __init__(self, thread_id: str = "D_test001", name: str | None = None):
        self.id = thread_id
        self.name = name or f"Thread {thread_id}"
        self.created_at = "2024-01-01T00:00:00Z"
        self.updated_at = "2024-01-01T00:00:00Z"
        self.cells = []


def create_mock_client():
    """Create a fully mocked LouieClient for testing."""

    # Create a wrapper class that makes Mock callable
    class CallableMock(Mock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._call_func = None

        def __call__(self, *args, **kwargs):
            if self._call_func:
                return self._call_func(*args, **kwargs)
            return super().__call__(*args, **kwargs)

    client = CallableMock()

    # Set up authentication manager mock with proper credentials structure
    auth_manager = Mock()
    auth_manager._credentials = {
        "username": "test_user",
        "password": "test_password",
        "api_key": "test_api_key",
        "personal_key_id": "test_personal_key_id",
        "personal_key_secret": "test_personal_key_secret",
        "org_name": "test_org",
        "api": 3,
        "server": "test.graphistry.com",
    }
    auth_manager.get_token.return_value = "fake-token-123"
    client._auth_manager = auth_manager

    # Mock _get_headers method
    def mock_get_headers():
        return {
            "Authorization": "Bearer fake-token-123",
            "X-Graphistry-Org": "test-org",
        }

    client._get_headers = Mock(return_value=mock_get_headers())

    # Thread management
    thread_counter = 0
    threads = {}

    def create_thread(name=None, initial_prompt=None):
        nonlocal thread_counter
        thread_counter += 1
        thread_id = f"D_test{thread_counter:03d}"

        thread = MockThread(thread_id, name)
        threads[thread_id] = thread

        if initial_prompt:
            # Create initial response
            response = create_mock_response("text", thread_id)
            thread._initial_response = response
            return thread

        return thread

    def add_cell(thread_id, prompt, agent="LouieAgent", traces=False):
        if not thread_id:
            thread = create_thread()
            thread_id = thread.id

        # Determine response type based on prompt
        response_type = determine_response_type(prompt)
        return create_mock_response(response_type, thread_id)

    def list_threads(page=1, page_size=20):
        return list(threads.values())[:page_size]

    def get_thread(thread_id):
        # If the thread doesn't exist, create a mock one for testing
        if thread_id not in threads:
            thread = MockThread(thread_id, f"Mock Thread {thread_id}")
            threads[thread_id] = thread
        return threads.get(thread_id)

    # Set up client methods
    client.create_thread = Mock(side_effect=create_thread)
    client.add_cell = Mock(side_effect=add_cell)
    client.list_threads = Mock(side_effect=list_threads)
    client.get_thread = Mock(side_effect=get_thread)
    client.register = Mock(return_value=client)

    # Make client callable (for v0.2.0+ interface)
    def client_call(prompt, *args, **kwargs):
        thread_id = kwargs.get("thread_id", "")
        agent = kwargs.get("agent", "LouieAgent")
        traces = kwargs.get("traces", False)
        return add_cell(thread_id, prompt, agent, traces)

    # Set the callable function
    client._call_func = client_call

    return client


def create_mock_response(response_type: str, thread_id: str) -> MockResponse:
    """Create a mock response of the specified type."""
    return MockResponse(response_type, thread_id)


def determine_response_type(prompt: str) -> str:
    """Determine response type based on prompt content."""
    prompt_lower = prompt.lower()

    if any(
        word in prompt_lower
        for word in [
            "dataframe",
            "query",
            "data",
            "table",
            "sql",
            "ip addresses",
            "find",
            "suspicious",
        ]
    ):
        return "dataframe"
    elif any(
        word in prompt_lower for word in ["graph", "visualiz", "network", "graphistry"]
    ):
        return "graph"
    elif any(word in prompt_lower for word in ["chart", "plot", "matplotlib"]):
        return "image"
    elif any(word in prompt_lower for word in ["error", "exception", "fail"]):
        return "exception"
    else:
        return "text"


class MockJSONLResponse:
    """Mock JSONL streaming response."""

    def __init__(self, elements: list[dict[str, Any]]):
        self.elements = elements
        self._lines = []
        for elem in elements:
            self._lines.append(json.dumps(elem))

    def iter_lines(self):
        """Iterate over JSONL lines."""
        for line in self._lines:
            yield line.encode("utf-8")

    @property
    def text(self):
        """Get full text response."""
        return "\n".join(self._lines)


def create_mock_jsonl_response(thread_id: str, prompt: str) -> MockJSONLResponse:
    """Create a mock JSONL response for API testing."""
    elements = [
        {
            "id": "B_text_001",
            "type": "TextElement",
            "text": "Processing your request...",
            "thread_id": thread_id,
            "status": "streaming",
        },
        {
            "id": "B_text_001",
            "type": "TextElement",
            "text": "Processing your request...\nAnalyzing data...",
            "thread_id": thread_id,
            "status": "streaming",
        },
        {
            "id": "B_text_001",
            "type": "TextElement",
            "text": "Processing your request...\nAnalyzing data...\nComplete!",
            "thread_id": thread_id,
            "status": "completed",
        },
    ]

    # Add specific elements based on prompt
    response_type = determine_response_type(prompt)
    if response_type == "dataframe":
        elements.append(
            {
                "id": "B_df_001",
                "type": "DfElement",
                "df_id": "df_123",
                "thread_id": thread_id,
                "metadata": {"shape": [10, 3], "columns": ["id", "name", "value"]},
            }
        )

    return MockJSONLResponse(elements)
