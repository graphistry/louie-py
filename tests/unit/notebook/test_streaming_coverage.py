"""Tests to improve coverage of streaming.py module."""

from unittest.mock import Mock, patch

from louieai.notebook.streaming import StreamingDisplay


class TestStreamingDisplayCoverage:
    """Test additional StreamingDisplay functionality for coverage."""

    def test_format_warning_line(self):
        """Test formatting of WarningLine elements."""
        display = StreamingDisplay()

        elem = {"type": "WarningLine", "text": "This is a warning message"}

        result = display._format_element(elem)
        assert "⚠️" in result
        assert "This is a warning message" in result
        assert "color: #ff8800" in result

    def test_format_error_line(self):
        """Test formatting of ErrorLine elements."""
        display = StreamingDisplay()

        elem = {"type": "ErrorLine", "text": "This is an error message"}

        result = display._format_element(elem)
        assert "❌" in result
        assert "This is an error message" in result
        assert "color: #cc0000" in result

    def test_format_code_element(self):
        """Test formatting of CodeElement."""
        display = StreamingDisplay()

        # Test with 'code' field
        elem = {
            "type": "CodeElement",
            "code": "def hello():\n    return 'world'",
            "language": "python",
        }

        result = display._format_element(elem)
        assert "<pre" in result
        assert "<code>" in result
        assert "def hello():" in result
        assert "return 'world'" in result

        # Test with 'text' field fallback
        elem2 = {"type": "CodeElement", "text": "print('hello')"}

        result2 = display._format_element(elem2)
        assert "print('hello')" in result2

    def test_format_graph_element_with_graphistry(self):
        """Test formatting of GraphElement with Graphistry integration."""
        mock_client = Mock()
        mock_client.plot = Mock(
            return_value=Mock(
                _repr_html_=Mock(return_value="<iframe>Graph visualization</iframe>")
            )
        )

        display = StreamingDisplay(client=mock_client)

        elem = {
            "type": "GraphElement",
            "value": {"dataset_id": "graph_123"},
            "nodes": [{"id": 1}],
            "edges": [{"source": 0, "target": 1}],
        }

        result = display._format_element(elem)
        assert "graph_123" in result  # dataset_id should be in URL

    def test_format_graph_element_without_graphistry(self):
        """Test formatting of GraphElement without Graphistry."""
        display = StreamingDisplay()

        elem = {
            "type": "graph",
            "dataset_id": "graph_456",
            "nodes": [{"id": 1}],
            "edges": [],
        }

        result = display._format_element(elem)
        assert "graph_456" in result  # dataset_id should be in result

    def test_format_base64_image_element(self):
        """Test formatting of Base64ImageElement."""
        display = StreamingDisplay()

        elem = {
            "type": "Base64ImageElement",
            "src": "data:image/png;base64,iVBORw0KGgo=",
            "width": 300,
            "height": 200,
        }

        result = display._format_element(elem)
        assert "<img" in result
        assert "data:image/png;base64" in result
        assert "width: 300px" in result
        assert "height: 200px" in result

    def test_format_binary_element_image(self):
        """Test formatting of BinaryElement with image content."""
        display = StreamingDisplay()

        elem = {
            "type": "BinaryElement",
            "url": "/api/file/123",
            "content_type": "image/png",
            "filename": "screenshot.png",
            "size": 1024,
        }

        result = display._format_element(elem)
        assert "<img" in result
        assert "Download screenshot.png" in result
        assert "📥" in result

    def test_format_binary_element_non_image(self):
        """Test formatting of BinaryElement with non-image content."""
        display = StreamingDisplay()

        elem = {
            "type": "BinaryElement",
            "url": "/api/file/456",
            "content_type": "application/pdf",
            "filename": "report.pdf",
            "size": 1048576,  # 1MB
        }

        result = display._format_element(elem)
        assert "📎 report.pdf" in result
        assert "1.0 MB" in result
        assert "Download" in result

    def test_format_markdown_element(self):
        """Test formatting of MarkdownElement."""
        display = StreamingDisplay()

        elem = {
            "type": "MarkdownElement",
            "markdown": "# Hello\n\nThis is **bold** text.",
        }

        # MarkdownElement not explicitly handled - falls to default
        result = display._format_element(elem)
        assert "MarkdownElement" in result

    def test_format_markdown_element_no_markdown_lib(self):
        """Test MarkdownElement when markdown library is not available."""
        display = StreamingDisplay()

        elem = {"type": "MarkdownElement", "markdown": "# Hello World"}

        # The MarkdownElement type is not explicitly handled, falls to default
        result = display._format_element(elem)
        # Should fall through to default handler
        assert "MarkdownElement" in result

    def test_format_table_element(self):
        """Test formatting of TableElement."""
        display = StreamingDisplay()

        elem = {
            "type": "TableElement",
            "headers": ["Name", "Age"],
            "rows": [["Alice", "30"]],
        }

        # TableElement is not explicitly handled, falls to default
        result = display._format_element(elem)
        assert "TableElement" in result

    def test_format_json_element(self):
        """Test formatting of JSONElement."""
        display = StreamingDisplay()

        elem = {"type": "JSONElement", "data": {"key": "value"}}

        # JSONElement is not explicitly handled, falls to default
        result = display._format_element(elem)
        assert "JSONElement" in result

    def test_format_unknown_element(self):
        """Test formatting of unknown element types."""
        display = StreamingDisplay()

        elem = {"type": "UnknownType", "text": "some text"}

        result = display._format_element(elem)
        assert "UnknownType" in result
        assert "some text" in result

    def test_update_method(self):
        """Test update method."""
        display = StreamingDisplay()

        # Test thread_id update
        data = {"dthread_id": "thread_123"}
        display.update(data)
        assert display.thread_id == "thread_123"

        # Test payload update
        data2 = {"payload": {"id": "1", "type": "text", "text": "Hello"}}
        display.update(data2)
        assert "1" in display.elements_by_id
        assert display.elements_by_id["1"]["text"] == "Hello"

    def test_render_html(self):
        """Test HTML rendering."""
        display = StreamingDisplay()
        display.thread_id = "thread_123"

        display.elements_by_id = {
            "1": {"type": "text", "text": "Hello"},
            "2": {"type": "ErrorLine", "text": "Error!"},
        }

        html = display._render_html()
        assert "thread_123" in html
        assert "Hello" in html
        assert "Error!" in html
        assert "❌" in html

    @patch("louieai.notebook.streaming.HAS_IPYTHON", True)
    @patch("louieai.notebook.streaming.display")
    @patch("louieai.notebook.streaming.update_display")
    def test_finalize_with_ipython(self, mock_update, mock_display):
        """Test finalize with IPython available."""
        display = StreamingDisplay(display_id="test_id")
        display.elements_by_id = {"1": {"type": "text", "text": "Test"}}

        display.finalize()

        # Should use update_display when display_id is set
        if display.display_id:
            mock_update.assert_called()
        else:
            mock_display.assert_called()

    @patch("louieai.notebook.streaming.HAS_IPYTHON", False)
    def test_finalize_without_ipython(self):
        """Test finalize when IPython is not available."""
        display = StreamingDisplay()
        display.elements_by_id = {"1": {"type": "text", "text": "Test"}}

        # Should not raise error
        display.finalize()

    def test_update_with_thread_id(self):
        """Test update with thread_id."""
        display = StreamingDisplay()

        data = {"dthread_id": "t_123"}
        display.update(data)
        assert display.thread_id == "t_123"

    def test_update_with_payload(self):
        """Test update with payload."""
        display = StreamingDisplay()

        data = {"payload": {"id": "1", "type": "text", "text": "Hello"}}
        display.update(data)
        assert "1" in display.elements_by_id
        assert display.elements_by_id["1"]["text"] == "Hello"

    def test_finalize_updates_display(self):
        """Test that finalize updates the display."""
        display = StreamingDisplay()
        display.thread_id = "test"
        display.elements_by_id = {"1": {"type": "text", "text": "Final"}}

        with patch("louieai.notebook.streaming.HAS_IPYTHON", False):
            # Should complete without error even without IPython
            display.finalize()

    def test_format_graph_element_dataset_id_locations(self):
        """Test different dataset_id locations in graph elements."""
        display = StreamingDisplay()

        # Test dataset_id in value
        elem1 = {"type": "graph", "value": {"dataset_id": "id_in_value"}}
        result1 = display._format_element(elem1)
        assert "id_in_value" in result1

        # Test dataset_id at root
        elem2 = {"type": "graph", "dataset_id": "id_at_root"}
        result2 = display._format_element(elem2)
        assert "id_at_root" in result2

        # Test fallback to id
        elem3 = {"type": "graph", "id": "fallback_id"}
        result3 = display._format_element(elem3)
        assert "fallback_id" in result3 or "Graph" in result3
