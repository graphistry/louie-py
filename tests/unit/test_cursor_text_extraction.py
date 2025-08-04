"""Unit tests for cursor text extraction with multiple field names."""

from louieai._client import Response
from louieai.notebook.cursor import ResponseProxy


class TestCursorTextExtraction:
    """Test that cursor correctly extracts text from various field names."""

    def test_text_field_extraction(self):
        """Test extraction from 'text' field."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "TextElement", "text": "Hello from text field"},
                {"type": "text", "text": "Another text field"},
            ],
        )
        proxy = ResponseProxy(response)

        texts = proxy.texts
        assert len(texts) == 2
        assert texts[0] == "Hello from text field"
        assert texts[1] == "Another text field"
        assert proxy.text == "Another text field"  # Last text

    def test_value_field_extraction(self):
        """Test extraction from 'value' field (new format)."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "text", "value": "Hello from value field"},
                {"type": "text", "value": "Another value field"},
            ],
        )
        proxy = ResponseProxy(response)

        texts = proxy.texts
        assert len(texts) == 2
        assert texts[0] == "Hello from value field"
        assert texts[1] == "Another value field"

    def test_content_field_extraction(self):
        """Test extraction from 'content' field (legacy format)."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "TextElement", "content": "Hello from content field"},
            ],
        )
        proxy = ResponseProxy(response)

        texts = proxy.texts
        assert len(texts) == 1
        assert texts[0] == "Hello from content field"

    def test_field_priority(self):
        """Test field priority: content > text > value."""
        response = Response(
            thread_id="test",
            elements=[
                # content takes priority
                {
                    "type": "text",
                    "content": "Content wins",
                    "text": "Text loses",
                    "value": "Value loses",
                },
                # text takes priority over value
                {"type": "text", "text": "Text wins", "value": "Value loses"},
                # value is used when others missing
                {"type": "text", "value": "Value only"},
            ],
        )
        proxy = ResponseProxy(response)

        texts = proxy.texts
        assert len(texts) == 3
        assert texts[0] == "Content wins"
        assert texts[1] == "Text wins"
        assert texts[2] == "Value only"

    def test_empty_text_handling(self):
        """Test handling of empty or missing text fields."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "text", "value": ""},  # Empty string
                {"type": "text"},  # No text field
                {"type": "text", "value": "Valid text"},
                {"type": "text", "text": None},  # None value
            ],
        )
        proxy = ResponseProxy(response)

        texts = proxy.texts
        assert len(texts) == 4
        assert texts[0] == ""  # Empty string preserved
        assert texts[1] == ""  # Missing field becomes empty
        assert texts[2] == "Valid text"
        assert texts[3] == ""  # None becomes empty

    def test_non_text_elements_ignored(self):
        """Test that non-text elements are filtered out."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "text", "value": "Text 1"},
                {"type": "df", "id": "df_123"},  # Should be ignored
                {"type": "TextElement", "text": "Text 2"},
                {"type": "graph", "id": "g_123"},  # Should be ignored
            ],
        )
        proxy = ResponseProxy(response)

        texts = proxy.texts
        assert len(texts) == 2
        assert texts[0] == "Text 1"
        assert texts[1] == "Text 2"

    def test_no_text_elements(self):
        """Test response with no text elements."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "df", "id": "df_123"},
                {"type": "graph", "id": "g_123"},
            ],
        )
        proxy = ResponseProxy(response)

        assert proxy.texts == []
        assert proxy.text is None

    def test_mixed_formats(self):
        """Test mixed old and new formats together."""
        response = Response(
            thread_id="test",
            elements=[
                {"type": "TextElement", "text": "Old format with text"},
                {"type": "text", "value": "New format with value"},
                {"type": "TextElement", "content": "Old format with content"},
                {"type": "text", "text": "New format with text"},
            ],
        )
        proxy = ResponseProxy(response)

        texts = proxy.texts
        assert len(texts) == 4
        assert all(isinstance(t, str) for t in texts)
        assert proxy.text == "New format with text"  # Last element
