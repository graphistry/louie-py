"""Tests for mock response library to ensure mocks are realistic."""

import json

import pytest

from .mock_responses import (
    MockResponseLibrary,
    MockStreamingResponse,
    ResponseScenarios,
    create_mock_api_response,
)


@pytest.mark.unit
class TestMockResponseLibrary:
    """Test the mock response library itself."""

    def test_text_response(self):
        """Test text response creation."""
        response = MockResponseLibrary.text_response("Hello, world!")

        assert response["type"] == "TextElement"
        assert response["text"] == "Hello, world!"
        assert response["thread_id"] == "D_test001"
        assert "created_at" in response
        assert response["status"] == "completed"

    def test_dataframe_response(self):
        """Test DataFrame response creation."""
        response = MockResponseLibrary.dataframe_response(
            shape=(50, 3), columns=["id", "name", "value"]
        )

        assert response["type"] == "DfElement"
        assert response["metadata"]["shape"] == [50, 3]
        assert response["metadata"]["columns"] == ["id", "name", "value"]
        assert "df_id" in response

    def test_graph_response(self):
        """Test graph response creation."""
        response = MockResponseLibrary.graph_response(num_nodes=100, num_edges=200)

        assert response["type"] == "GraphElement"
        assert response["metadata"]["num_nodes"] == 100
        assert response["metadata"]["num_edges"] == 200
        assert "dataset_id" in response
        assert "url" in response

    def test_exception_response(self):
        """Test exception response creation."""
        response = MockResponseLibrary.exception_response(
            error_type="ValueError", message="Invalid input"
        )

        assert response["type"] == "ExceptionElement"
        assert response["error_type"] == "ValueError"
        assert response["message"] == "Invalid input"
        assert response["status"] == "error"
        assert "traceback" in response


@pytest.mark.unit
class TestMockStreamingResponse:
    """Test streaming response behavior."""

    def test_text_streaming(self):
        """Test that text elements stream progressively."""
        elements = [MockResponseLibrary.text_response("Hello world from Louie")]

        streamer = MockStreamingResponse(elements)
        lines = list(streamer.iter_lines())

        # Should have multiple lines for progressive text
        assert len(lines) > 1

        # Parse lines
        parsed = [json.loads(line) for line in lines]

        # First lines should be streaming
        assert parsed[0]["status"] == "streaming"
        assert "Hello" in parsed[0]["text"]

        # Last line should be completed
        assert parsed[-1]["status"] == "completed"
        assert parsed[-1]["text"] == "Hello world from Louie"

    def test_non_text_streaming(self):
        """Test that non-text elements are sent complete."""
        elements = [MockResponseLibrary.dataframe_response()]

        streamer = MockStreamingResponse(elements)
        lines = list(streamer.iter_lines())

        # Should have exactly one line for non-text
        assert len(lines) == 1

        parsed = json.loads(lines[0])
        assert parsed["type"] == "DfElement"
        assert parsed["status"] == "completed"


@pytest.mark.unit
class TestResponseScenarios:
    """Test pre-built response scenarios."""

    def test_simple_question_scenario(self):
        """Test simple question response."""
        elements = ResponseScenarios.simple_question()

        assert len(elements) == 1
        assert elements[0]["type"] == "TextElement"
        assert "Paris" in elements[0]["text"]

    def test_data_query_scenario(self):
        """Test data query response sequence."""
        elements = ResponseScenarios.data_query()

        # Should have: intro text, call, dataframe, summary text
        assert len(elements) == 4

        types = [e["type"] for e in elements]
        assert types == ["TextElement", "CallElement", "DfElement", "TextElement"]

        # Check call element
        call_elem = elements[1]
        assert call_elem["function"] == "query_postgresql"
        assert "query" in call_elem["args"]

        # Check dataframe element
        df_elem = elements[2]
        assert df_elem["metadata"]["shape"] == [100, 5]

    def test_visualization_scenario(self):
        """Test visualization response sequence."""
        elements = ResponseScenarios.visualization_request()

        # Should have: intro, call, graph, summary
        assert len(elements) == 4

        # Find graph element
        graph_elem = next(e for e in elements if e["type"] == "GraphElement")
        assert graph_elem["metadata"]["num_nodes"] == 500
        assert graph_elem["metadata"]["num_edges"] == 1200

    def test_error_scenario(self):
        """Test error handling response."""
        elements = ResponseScenarios.error_scenario()

        # Should have: intro, exception, recovery text
        assert len(elements) == 3

        # Find exception element
        exc_elem = next(e for e in elements if e["type"] == "ExceptionElement")
        assert exc_elem["error_type"] == "DatabaseConnectionError"
        assert "timeout" in exc_elem["message"].lower()

    def test_multi_step_analysis(self):
        """Test complex multi-step analysis."""
        elements = ResponseScenarios.multi_step_analysis()

        # Should have multiple steps
        assert len(elements) > 5

        # Check for variety of element types
        types = {e["type"] for e in elements}
        assert "TextElement" in types
        assert "CallElement" in types
        assert "DfElement" in types
        assert "Base64ImageElement" in types

        # Final element should be comprehensive summary
        final_text = elements[-1]["text"]
        assert "Summary" in final_text
        assert "Recommendations" in final_text


@pytest.mark.unit
class TestMockAPIResponse:
    """Test query-based response generation."""

    def test_data_query_detection(self):
        """Test that data queries return appropriate responses."""
        response = create_mock_api_response("Show me customer data from last month")

        elements = []
        for line in response.iter_lines():
            elements.append(json.loads(line))

        # Should include dataframe
        types = [e["type"] for e in elements]
        assert "DfElement" in types

    def test_visualization_query_detection(self):
        """Test that viz queries return appropriate responses."""
        response = create_mock_api_response(
            "Create a network graph of user connections"
        )

        elements = []
        for line in response.iter_lines():
            elements.append(json.loads(line))

        # Should include graph
        types = [e["type"] for e in elements]
        assert "GraphElement" in types

    def test_simple_query_default(self):
        """Test that simple queries get simple responses."""
        response = create_mock_api_response("What is the weather today?")

        elements = []
        for line in response.iter_lines():
            elements.append(json.loads(line))

        # Should be mostly text
        types = [e["type"] for e in elements]
        assert all(t == "TextElement" for t in types)
