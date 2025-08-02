"""Unit tests for streaming display functionality."""

from unittest.mock import Mock, patch

import pytest

from louieai.notebook.streaming import StreamingDisplay, stream_response


class TestStreamingDisplay:
    """Test StreamingDisplay class."""

    def test_init(self):
        """Test StreamingDisplay initialization."""
        display = StreamingDisplay()
        assert display.display_id is None
        assert display.elements_by_id == {}
        assert display.thread_id is None
        assert display.start_time > 0

    def test_format_text_element(self):
        """Test formatting text elements."""
        display = StreamingDisplay()
        elem = {"type": "TextElement", "text": "Hello\nWorld"}

        formatted = display._format_element(elem)
        assert "Hello<br>World" in formatted

    def test_format_df_element(self):
        """Test formatting dataframe elements."""
        display = StreamingDisplay()
        elem = {"type": "DfElement", "df_id": "df_123", "metadata": {"shape": [10, 3]}}

        formatted = display._format_element(elem)
        assert "DataFrame: df_123" in formatted
        assert "10 x 3" in formatted

    def test_format_error_element(self):
        """Test formatting error elements."""
        display = StreamingDisplay()
        elem = {"type": "ExceptionElement", "message": "Test error"}

        formatted = display._format_element(elem)
        assert "Error: Test error" in formatted
        assert "color: red" in formatted

    def test_update_thread_id(self):
        """Test updating with thread ID."""
        display = StreamingDisplay()
        data = {"dthread_id": "D_test123"}

        display.update(data)
        assert display.thread_id == "D_test123"

    def test_update_element(self):
        """Test updating with element payload."""
        display = StreamingDisplay()
        data = {"payload": {"id": "B_001", "type": "TextElement", "text": "Hello"}}

        display.update(data)
        assert "B_001" in display.elements_by_id
        assert display.elements_by_id["B_001"]["text"] == "Hello"

    @patch("louieai.notebook.streaming.HAS_IPYTHON", True)
    @patch("louieai.notebook.streaming.update_display")
    @patch("louieai.notebook.streaming.HTML")
    def test_update_with_display(self, mock_html, mock_update):
        """Test display update in Jupyter environment."""
        display = StreamingDisplay(display_id="test_id")

        # First update
        data = {"dthread_id": "D_test123"}
        display.update(data)

        # Should update display
        mock_html.assert_called_once()
        mock_update.assert_called_once()

        # Verify HTML content
        html_call = mock_html.call_args[0][0]
        assert "D_test123" in html_call

    @patch("louieai.notebook.streaming.HAS_IPYTHON", True)
    @patch("louieai.notebook.streaming.clear_output")
    @patch("louieai.notebook.streaming.display")
    @patch("louieai.notebook.streaming.HTML")
    def test_update_without_display_id(self, mock_html, mock_display, mock_clear):
        """Test display update without display ID (uses clear_output)."""
        display = StreamingDisplay()

        data = {"dthread_id": "D_test123"}
        display.update(data)

        # Should clear and display
        mock_clear.assert_called_once_with(wait=True)
        mock_display.assert_called_once()

    def test_update_throttling(self):
        """Test that updates are throttled."""
        display = StreamingDisplay()

        with (
            patch("louieai.notebook.streaming.HAS_IPYTHON", True),
            patch("louieai.notebook.streaming.clear_output") as mock_clear,
            patch("time.time") as mock_time,
        ):
            # Set initial time
            display.start_time = 0
            display.last_update_time = 0

            # First update at time 0.5
            mock_time.return_value = 0.5
            display.update({"dthread_id": "D_test"})
            assert mock_clear.call_count == 1

            # Second update at 0.55 (too soon - only 0.05s later)
            mock_time.return_value = 0.55
            display.update(
                {
                    "payload": {
                        "id": "B_001",
                        "type": "TextElement",
                        "text": "Hi",
                    }
                }
            )
            assert mock_clear.call_count == 1  # Should not update

            # Third update at 0.65 (0.15s after first - should update)
            mock_time.return_value = 0.65
            display.update(
                {
                    "payload": {
                        "id": "B_002",
                        "type": "TextElement",
                        "text": "Hello",
                    }
                }
            )
            assert mock_clear.call_count == 2  # Should update


class TestStreamResponse:
    """Test stream_response function."""

    @pytest.fixture
    def mock_client(self):
        """Create mock client."""
        client = Mock()
        client.server_url = "https://test.louie.ai"
        client._get_headers.return_value = {"Authorization": "Bearer test"}
        client._fetch_dataframe_arrow.return_value = None
        return client

    def test_basic_streaming(self, mock_client):
        """Test basic streaming response."""
        # Mock response lines
        lines = [
            '{"dthread_id": "D_test123"}',
            '{"payload": {"id": "B_001", "type": "TextElement", "text": "Hello"}}',
            '{"payload": {"id": "B_001", "type": "TextElement", '
            '"text": "Hello World"}}',
        ]

        # Mock httpx
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines.return_value = iter(lines)

        mock_stream_cm = Mock()
        mock_stream_cm.__enter__ = Mock(return_value=mock_response)
        mock_stream_cm.__exit__ = Mock(return_value=None)

        with patch("httpx.Client") as mock_httpx:
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            # Call stream_response
            result = stream_response(mock_client, thread_id="", prompt="Test query")

        # Verify result
        assert result["dthread_id"] == "D_test123"
        assert len(result["elements"]) == 1
        assert result["elements"][0]["text"] == "Hello World"

    def test_streaming_with_dataframe(self, mock_client):
        """Test streaming with dataframe element."""
        lines = [
            '{"dthread_id": "D_test123"}',
            '{"payload": {"id": "B_001", "type": "TextElement", "text": "Data:"}}',
            '{"payload": {"id": "B_002", "type": "DfElement", "df_id": "df_456"}}',
        ]

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines.return_value = iter(lines)

        mock_stream_cm = Mock()
        mock_stream_cm.__enter__ = Mock(return_value=mock_response)
        mock_stream_cm.__exit__ = Mock(return_value=None)

        with patch("httpx.Client") as mock_httpx:
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            result = stream_response(
                mock_client, thread_id="D_test123", prompt="Show data"
            )

        # Verify dataframe fetch was attempted
        mock_client._fetch_dataframe_arrow.assert_called_once_with(
            "D_test123", "df_456"
        )

        # Verify result
        assert len(result["elements"]) == 2
        assert result["elements"][1]["type"] == "DfElement"

    def test_streaming_error_handling(self, mock_client):
        """Test error handling during streaming."""
        # Mock httpx to raise error
        with patch("httpx.Client") as mock_httpx:
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.side_effect = Exception("Network error")
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            # Should raise and display error
            with pytest.raises(Exception, match="Network error"):
                stream_response(mock_client, thread_id="", prompt="Test")

    @patch("louieai.notebook.streaming.HAS_IPYTHON", True)
    @patch("louieai.notebook.streaming.StreamingDisplay")
    def test_display_updates(self, mock_display_class, mock_client):
        """Test that display is updated during streaming."""
        # Create mock display instance
        mock_display = Mock()
        mock_display_class.return_value = mock_display

        lines = [
            '{"dthread_id": "D_test123"}',
            '{"payload": {"id": "B_001", "type": "TextElement", "text": "Line 1"}}',
            '{"payload": {"id": "B_001", "type": "TextElement", '
            '"text": "Line 1\\nLine 2"}}',
        ]

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines.return_value = iter(lines)

        mock_stream_cm = Mock()
        mock_stream_cm.__enter__ = Mock(return_value=mock_response)
        mock_stream_cm.__exit__ = Mock(return_value=None)

        with patch("httpx.Client") as mock_httpx:
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            stream_response(mock_client, "", "Test")

        # Verify display was updated for each line
        assert mock_display.update.call_count == 3

        # Verify finalize was called
        mock_display.finalize.assert_called_once()
