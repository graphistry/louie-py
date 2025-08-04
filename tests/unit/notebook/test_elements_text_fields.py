"""Test that elements property handles different text field names correctly."""

import pandas as pd

from louieai._client import Response
from louieai.notebook.cursor import ResponseProxy


class TestElementsTextFields:
    """Test that ResponseProxy.elements handles text fields correctly."""

    def test_text_element_with_content_field(self):
        """Test text element with 'content' field."""
        response = Response(
            thread_id="D_test",
            elements=[
                {"id": "B_001", "type": "TextElement", "content": "Hello from content"}
            ],
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        assert len(elements) == 1
        assert elements[0]["type"] == "text"
        assert elements[0]["value"] == "Hello from content"

    def test_text_element_with_text_field(self):
        """Test text element with 'text' field (DatabricksAgent case)."""
        response = Response(
            thread_id="D_test",
            elements=[
                {"id": "B_001", "type": "TextElement", "text": "Hello from text"}
            ],
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        assert len(elements) == 1
        assert elements[0]["type"] == "text"
        assert elements[0]["value"] == "Hello from text"

    def test_text_element_with_value_field(self):
        """Test text element with 'value' field."""
        response = Response(
            thread_id="D_test",
            elements=[
                {"id": "B_001", "type": "TextElement", "value": "Hello from value"}
            ],
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        assert len(elements) == 1
        assert elements[0]["type"] == "text"
        assert elements[0]["value"] == "Hello from value"

    def test_text_element_field_priority(self):
        """Test field priority: content > text > value."""
        # When all fields present, content should win
        response = Response(
            thread_id="D_test",
            elements=[
                {
                    "id": "B_001",
                    "type": "TextElement",
                    "content": "Content wins",
                    "text": "Text loses",
                    "value": "Value loses",
                }
            ],
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        assert elements[0]["value"] == "Content wins"

        # When no content, text should win
        response = Response(
            thread_id="D_test",
            elements=[
                {
                    "id": "B_001",
                    "type": "TextElement",
                    "text": "Text wins",
                    "value": "Value loses",
                }
            ],
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        assert elements[0]["value"] == "Text wins"

    def test_empty_text_elements_databricks_case(self):
        """Test the reported DatabricksAgent case with empty text."""
        # Simulate DatabricksAgent response with empty text fields
        response = Response(
            thread_id="D_test",
            elements=[
                {"id": "B_001", "type": "TextElement", "text": ""},
                {"id": "B_002", "type": "TextElement", "text": ""},
                {"id": "B_003", "type": "TextElement", "text": ""},
                {"id": "B_004", "type": "DfElement", "df_id": "databricks_result_456"},
            ],
        )

        # Add mock dataframe to simulate fetched data
        response.elements[3]["table"] = pd.DataFrame(
            {
                "ClientIP": ["107.77.213.173"],
                "CorrelationId": ["9e627e9e-d0dd-6000-daf9-da44fcd45d4e"],
                "CreationTime": ["2018-08-20T13:16:56"],
            }
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        # Should have 4 elements total
        assert len(elements) == 4

        # Text elements should have empty values
        text_elements = [e for e in elements if e["type"] == "text"]
        assert len(text_elements) == 3
        for elem in text_elements:
            assert elem["value"] == ""

        # DataFrame element should be present
        df_elements = [e for e in elements if e["type"] == "dataframe"]
        assert len(df_elements) == 1
        assert isinstance(df_elements[0]["value"], pd.DataFrame)

    def test_mixed_element_types(self):
        """Test elements with mixed types."""
        response = Response(
            thread_id="D_test",
            elements=[
                {"id": "B_001", "type": "TextElement", "text": "Some text"},
                {
                    "id": "B_002",
                    "type": "DfElement",
                    "table": pd.DataFrame({"a": [1, 2]}),
                },
                {
                    "id": "B_003",
                    "type": "ExceptionElement",
                    "message": "Error occurred",
                },
                {"id": "B_004", "type": "TextElement", "content": "More text"},
            ],
        )

        proxy = ResponseProxy(response)
        elements = proxy.elements

        # Should handle all element types
        assert len(elements) == 4

        # Group by type for easier checking
        errors = [e for e in elements if e["type"] == "error"]
        texts = [e for e in elements if e["type"] == "text"]
        dfs = [e for e in elements if e["type"] == "dataframe"]

        # Check we have the right counts
        assert len(errors) == 1
        assert len(texts) == 2
        assert len(dfs) == 1

        # Check error element
        assert errors[0]["value"] == "Error occurred"

        # Check text elements
        text_values = [t["value"] for t in texts]
        assert "Some text" in text_values
        assert "More text" in text_values

        # Check dataframe element
        assert isinstance(dfs[0]["value"], pd.DataFrame)

    def test_texts_property_consistency(self):
        """Verify texts property uses same logic as elements."""
        response = Response(
            thread_id="D_test",
            elements=[
                {"id": "B_001", "type": "TextElement", "text": "Text field"},
                {"id": "B_002", "type": "TextElement", "content": "Content field"},
                {"id": "B_003", "type": "TextElement", "value": "Value field"},
            ],
        )

        proxy = ResponseProxy(response)

        # Get values from both properties
        texts = proxy.texts
        text_elements = [e["value"] for e in proxy.elements if e["type"] == "text"]

        # Should be consistent
        assert texts == text_elements
        assert texts == ["Text field", "Content field", "Value field"]
