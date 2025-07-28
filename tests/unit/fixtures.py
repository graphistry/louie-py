"""Shared fixtures for unit tests."""

from unittest.mock import Mock, patch

import pytest

from .mock_responses import (
    MockResponseLibrary,
    ResponseScenarios,
    create_mock_api_response,
)
from .mocks import create_mock_client


@pytest.fixture
def mock_response_library():
    """Provide access to mock response library."""
    return MockResponseLibrary()


@pytest.fixture
def response_scenarios():
    """Provide access to pre-built response scenarios."""
    return ResponseScenarios()


@pytest.fixture
def mock_simple_response():
    """Mock a simple text response."""
    return MockResponseLibrary.text_response("This is a simple response to your query.")


@pytest.fixture
def mock_data_response():
    """Mock a response with DataFrame."""
    return ResponseScenarios.data_query()


@pytest.fixture
def mock_graph_response():
    """Mock a response with graph visualization."""
    return ResponseScenarios.visualization_request()


@pytest.fixture
def mock_error_response():
    """Mock an error response."""
    return ResponseScenarios.error_scenario()


@pytest.fixture
def mock_streaming_client():
    """Create a client that returns streaming responses."""
    client = create_mock_client()

    def mock_add_cell(thread_id, prompt, agent="LouieAgent"):
        # Create appropriate mock response based on prompt
        mock_response = create_mock_api_response(prompt, thread_id or "D_new001")

        # Collect all elements from streaming
        elements = []
        for line in mock_response.iter_lines():
            import json

            elements.append(json.loads(line))

        # Return last state of elements

        # Create a mock Response object
        response = Mock()
        response.thread_id = elements[0]["thread_id"] if elements else thread_id
        response.elements = elements

        # Add convenience properties
        response.text_elements = [e for e in elements if e.get("type") == "TextElement"]
        response.dataframe_elements = [
            e for e in elements if e.get("type") == "DfElement"
        ]
        response.graph_elements = [
            e for e in elements if e.get("type") == "GraphElement"
        ]
        response.error_elements = [
            e for e in elements if e.get("type") == "ExceptionElement"
        ]

        response.has_dataframes = len(response.dataframe_elements) > 0
        response.has_graphs = len(response.graph_elements) > 0
        response.has_errors = len(response.error_elements) > 0

        return response

    # Override add_cell to use our streaming mock
    client.add_cell = Mock(side_effect=mock_add_cell)

    return client


@pytest.fixture
def mock_authenticated_client(mock_graphistry):
    """Create a client with mocked authentication."""
    with patch("louieai.client.graphistry", mock_graphistry):
        client = create_mock_client()
        # Ensure auth methods work
        client._auth_manager = Mock()
        client._auth_manager.get_token = Mock(return_value="fake-token-123")
        client._auth_manager.handle_auth_error = Mock(return_value=False)
        return client


@pytest.fixture
def sample_thread():
    """Create a sample thread object."""
    from louieai.client import Thread

    return Thread(id="D_test001", name="Test Thread")


@pytest.fixture
def sample_responses():
    """Create sample response objects of different types."""
    return {
        "text": MockResponseLibrary.text_response("Sample text"),
        "dataframe": MockResponseLibrary.dataframe_response(),
        "graph": MockResponseLibrary.graph_response(),
        "error": MockResponseLibrary.exception_response(),
        "image": MockResponseLibrary.image_response(),
    }
