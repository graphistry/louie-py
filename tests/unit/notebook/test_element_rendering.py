"""Test rendering of various element types."""

from louieai._client import Response
from louieai.notebook.cursor import _render_response_html
from louieai.notebook.streaming import StreamingDisplay


class TestElementRendering:
    """Test that all element types render correctly."""

    def test_debug_line_rendering(self):
        """Test DebugLine elements are rendered with their text."""
        response = Response(
            thread_id="D_test",
            elements=[{"type": "DebugLine", "text": "Debug: Variable x = 42"}],
        )

        html = _render_response_html(response)
        assert "Debug: Variable x = 42" in html
        assert "🐛" in html

    def test_info_line_rendering(self):
        """Test InfoLine elements are rendered with their text."""
        response = Response(
            thread_id="D_test",
            elements=[{"type": "InfoLine", "text": "Info: Processing started"}],
        )

        html = _render_response_html(response)
        assert "Info: Processing started" in html
        assert "i " in html

    def test_warning_line_rendering(self):
        """Test WarningLine elements are rendered with their text."""
        response = Response(
            thread_id="D_test",
            elements=[{"type": "WarningLine", "text": "Warning: Deprecated function"}],
        )

        html = _render_response_html(response)
        assert "Warning: Deprecated function" in html
        assert "⚠️" in html

    def test_error_line_rendering(self):
        """Test ErrorLine elements are rendered with their text."""
        response = Response(
            thread_id="D_test",
            elements=[{"type": "ErrorLine", "text": "Error: File not found"}],
        )

        html = _render_response_html(response)
        assert "Error: File not found" in html
        assert "❌" in html

    def test_code_element_rendering(self):
        """Test CodeElement is rendered as code block."""
        response = Response(
            thread_id="D_test",
            elements=[
                {"type": "CodeElement", "code": "def hello():\n    print('Hello')"}
            ],
        )

        html = _render_response_html(response)
        assert "def hello():" in html
        assert "<pre" in html
        assert "<code>" in html

    def test_mixed_elements_rendering(self):
        """Test mixed element types render in order."""
        response = Response(
            thread_id="D_test",
            elements=[
                {"type": "TextElement", "text": "Here's the analysis:"},
                {"type": "InfoLine", "text": "Processing data..."},
                {"type": "DebugLine", "text": "Found 100 records"},
                {"type": "TextElement", "text": "Complete!"},
            ],
        )

        html = _render_response_html(response)

        # All elements should be present (check both escaped and unescaped)
        assert "the analysis:" in html  # May be escaped
        assert "Processing data..." in html
        assert "Found 100 records" in html
        assert "Complete!" in html

        # Check order (Info should come before Debug in the HTML)
        info_pos = html.find("Processing data...")
        debug_pos = html.find("Found 100 records")
        assert info_pos < debug_pos

    def test_streaming_display_debug_line(self):
        """Test StreamingDisplay formats DebugLine correctly."""
        display = StreamingDisplay()
        elem = {"type": "DebugLine", "text": "Debug message"}

        formatted = display._format_element(elem)
        assert "Debug message" in formatted
        assert "🐛" in formatted

    def test_streaming_display_info_line(self):
        """Test StreamingDisplay formats InfoLine correctly."""
        display = StreamingDisplay()
        elem = {"type": "InfoLine", "text": "Information"}

        formatted = display._format_element(elem)
        assert "Information" in formatted
        assert "i " in formatted

    def test_unknown_element_with_text(self):
        """Test unknown elements show their text."""
        response = Response(
            thread_id="D_test",
            elements=[{"type": "CustomElement", "text": "Custom content"}],
        )

        html = _render_response_html(response)
        assert "[CustomElement] Custom content" in html

    def test_element_without_text(self):
        """Test elements without text don't crash."""
        response = Response(
            thread_id="D_test",
            elements=[
                {"type": "EmptyElement"},
                {"type": "TextElement", "text": "After empty"},
            ],
        )

        html = _render_response_html(response)
        assert "After empty" in html  # Should still render other elements
