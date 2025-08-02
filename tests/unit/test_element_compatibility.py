"""Unit tests for element type compatibility.

Tests to ensure we handle both old (CamelCase) and new (lowercase) element formats.
"""

import pandas as pd

from louieai._client import Response


class TestElementTypeCompatibility:
    """Test that Response handles both old and new element formats."""

    def test_text_element_camelcase(self):
        """Test TextElement (old format) is recognized."""
        elements = [
            {"type": "TextElement", "text": "Hello world"},
            {"type": "TextElement", "content": "Another text"},
        ]
        response = Response(thread_id="test", elements=elements)

        assert len(response.text_elements) == 2
        assert response.has_dataframes is False
        assert response.has_errors is False

    def test_text_element_lowercase(self):
        """Test text element (new format) is recognized."""
        elements = [
            {"type": "text", "value": "Hello world"},
            {"type": "text", "text": "Another text"},
        ]
        response = Response(thread_id="test", elements=elements)

        assert len(response.text_elements) == 2
        assert response.has_dataframes is False

    def test_mixed_text_formats(self):
        """Test mixed TextElement and text formats."""
        elements = [
            {"type": "TextElement", "text": "Old format"},
            {"type": "text", "value": "New format"},
        ]
        response = Response(thread_id="test", elements=elements)

        assert len(response.text_elements) == 2

    def test_df_element_camelcase(self):
        """Test DfElement (old format) is recognized."""
        elements = [
            {"type": "DfElement", "df_id": "df_123", "metadata": {"shape": [10, 5]}},
        ]
        response = Response(thread_id="test", elements=elements)

        assert len(response.dataframe_elements) == 1
        assert response.has_dataframes is True
        assert response.has_graphs is False

    def test_df_element_lowercase(self):
        """Test df element (new format) is recognized."""
        elements = [
            {"type": "df", "id": "df_123", "metadata": {"shape": [10, 5]}},
            {"type": "df", "block_id": "block_456"},
        ]
        response = Response(thread_id="test", elements=elements)

        assert len(response.dataframe_elements) == 2
        assert response.has_dataframes is True

    def test_graph_element_formats(self):
        """Test both GraphElement and graph formats."""
        elements = [
            {"type": "GraphElement", "id": "g1"},
            {"type": "graph", "id": "g2"},
        ]
        response = Response(thread_id="test", elements=elements)

        assert len(response.graph_elements) == 2
        assert response.has_graphs is True
        # Verify elements are preserved
        assert response.graph_elements[0]["id"] == "g1"
        assert response.graph_elements[1]["id"] == "g2"

    def test_error_element_formats(self):
        """Test various error element formats."""
        elements = [
            {"type": "ExceptionElement", "message": "Error 1"},
            {"type": "exception", "message": "Error 2"},
            {"type": "error", "message": "Error 3"},
        ]
        response = Response(thread_id="test", elements=elements)

        assert response.has_errors is True
        # Error elements are not exposed via a property, just has_errors

    def test_empty_response(self):
        """Test response with no elements."""
        response = Response(thread_id="test", elements=[])

        assert len(response.text_elements) == 0
        assert len(response.dataframe_elements) == 0
        assert len(response.graph_elements) == 0
        assert response.has_dataframes is False
        assert response.has_graphs is False
        assert response.has_errors is False

    def test_mixed_element_types(self):
        """Test response with mixed element types and formats."""
        elements = [
            {"type": "TextElement", "text": "Analysis complete"},
            {"type": "text", "value": "Here are the results:"},
            {"type": "DfElement", "df_id": "df_001"},
            {"type": "df", "id": "df_002"},
            {"type": "GraphElement", "id": "g_001"},
            {"type": "exception", "message": "Warning: Some data missing"},
        ]
        response = Response(thread_id="test", elements=elements)

        assert len(response.text_elements) == 2
        assert len(response.dataframe_elements) == 2
        assert len(response.graph_elements) == 1
        assert response.has_dataframes is True
        assert response.has_graphs is True
        assert response.has_errors is True

    def test_element_with_table(self):
        """Test DfElement with populated table data."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        elements = [
            {"type": "df", "id": "df_123", "table": df},
        ]
        response = Response(thread_id="test", elements=elements)

        assert len(response.dataframe_elements) == 1
        assert "table" in response.dataframe_elements[0]
        assert isinstance(response.dataframe_elements[0]["table"], pd.DataFrame)

    def test_unknown_element_type(self):
        """Test that unknown element types are ignored."""
        elements = [
            {"type": "TextElement", "text": "Known"},
            {"type": "UnknownElement", "data": "Something"},
            {"type": "df", "id": "df_123"},
        ]
        response = Response(thread_id="test", elements=elements)

        assert len(response.text_elements) == 1
        assert len(response.dataframe_elements) == 1
        # Unknown elements are kept in elements list but not categorized
        assert len(response.elements) == 3
