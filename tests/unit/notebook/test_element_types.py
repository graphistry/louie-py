"""Tests for additional element type support."""

from unittest.mock import Mock

import pandas as pd

from louieai import Response
from louieai.notebook.cursor import Cursor, ResponseProxy


class TestErrorElements:
    """Test error element handling."""

    def test_error_elements_extraction(self):
        """Test extraction of ExceptionElement from response."""
        # Create response with error elements
        response = Mock(spec=Response)
        response.elements = [
            {"type": "TextElement", "content": "Some text"},
            {
                "type": "ExceptionElement",
                "error_type": "ValueError",
                "message": "Invalid input",
                "traceback": "Traceback...",
                "id": "error-123",
            },
            {
                "type": "ExceptionElement",
                "error_type": "KeyError",
                "message": "Key not found",
                "id": "error-456",
            },
        ]
        response.text_elements = []
        response.dataframe_elements = []
        response.graph_elements = []

        proxy = ResponseProxy(response)

        # Check errors property
        errors = proxy.errors
        assert len(errors) == 2
        assert errors[0]["type"] == "ExceptionElement"
        assert errors[0]["message"] == "Invalid input"
        assert errors[1]["message"] == "Key not found"

        # Check has_errors
        assert proxy.has_errors is True

        # Check elements includes errors
        elements = proxy.elements
        error_elements = [e for e in elements if e["type"] == "error"]
        assert len(error_elements) == 2
        assert error_elements[0]["value"] == "Invalid input"
        assert error_elements[0]["error_type"] == "ValueError"

    def test_no_errors_case(self):
        """Test when response has no errors."""
        response = Mock(spec=Response)
        response.elements = [{"type": "TextElement", "content": "Success"}]
        response.text_elements = [{"type": "TextElement", "content": "Success"}]
        response.dataframe_elements = []
        response.graph_elements = []

        proxy = ResponseProxy(response)

        assert proxy.errors == []
        assert proxy.has_errors is False

        # Elements should only have text
        assert len(proxy.elements) == 1
        assert proxy.elements[0]["type"] == "text"

    def test_missing_elements_attribute(self):
        """Test handling when response lacks elements attribute."""
        response = Mock(spec=Response)
        response.text_elements = []
        response.dataframe_elements = []
        response.graph_elements = []
        # No elements attribute

        proxy = ResponseProxy(response)

        assert proxy.errors == []
        assert proxy.has_errors is False

    def test_global_cursor_error_access(self):
        """Test accessing errors through Cursor."""
        cursor = Cursor()

        # Mock response with errors
        response = Mock(spec=Response)
        response.elements = [
            {
                "type": "ExceptionElement",
                "message": "Database connection failed",
                "error_type": "ConnectionError",
            }
        ]
        response.text_elements = []
        response.dataframe_elements = []
        response.graph_elements = []

        cursor._history.append(response)

        # Test error access
        assert cursor.has_errors is True
        assert len(cursor.errors) == 1
        assert cursor.errors[0]["message"] == "Database connection failed"

        # Test elements includes errors
        error_elements = [e for e in cursor.elements if e["type"] == "error"]
        assert len(error_elements) == 1


class TestMixedElements:
    """Test handling of mixed element types."""

    def test_all_element_types_together(self):
        """Test response with all element types."""
        response = Mock(spec=Response)

        # Set up various elements
        df = pd.DataFrame({"x": [1, 2, 3]})
        response.text_elements = [
            {"type": "TextElement", "content": "Analysis complete"}
        ]
        response.dataframe_elements = [{"type": "DfElement", "table": df}]
        response.graph_elements = [{"type": "GraphElement", "nodes": [], "edges": []}]
        response.elements = [
            {"type": "TextElement", "content": "Analysis complete"},
            {"type": "DfElement", "table": df},
            {"type": "GraphElement", "nodes": [], "edges": []},
            {"type": "ExceptionElement", "message": "Warning: Some data missing"},
        ]

        proxy = ResponseProxy(response)

        # Check all elements are captured
        elements = proxy.elements
        types = {e["type"] for e in elements}
        assert types == {"text", "dataframe", "graph", "error"}

        # Check individual accessors
        assert proxy.text == "Analysis complete"
        assert proxy.df is not None
        assert len(proxy.errors) == 1
        assert proxy.has_errors is True

    def test_element_ordering(self):
        """Test that elements maintain consistent ordering."""
        response = Mock(spec=Response)
        response.elements = [{"type": "ExceptionElement", "message": "Error first"}]
        response.text_elements = [{"type": "TextElement", "content": "Then text"}]
        response.dataframe_elements = []
        response.graph_elements = []

        proxy = ResponseProxy(response)
        elements = proxy.elements

        # Errors should come first (from elements list)
        assert elements[0]["type"] == "error"
        assert elements[0]["value"] == "Error first"

        # Then text elements
        assert elements[1]["type"] == "text"
        assert elements[1]["value"] == "Then text"
