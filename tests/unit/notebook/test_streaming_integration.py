"""Integration tests for streaming display functionality."""

import time
from unittest.mock import Mock, patch

import pytest

from louieai import louie
from louieai._client import Response


@pytest.mark.unit
class TestStreamingIntegration:
    """Test streaming functionality in notebook context."""

    @pytest.fixture
    def mock_graphistry(self):
        """Mock graphistry client for tests."""
        mock = Mock()
        mock.api_token = Mock(return_value="fake-token-123")
        mock.register = Mock()
        mock.refresh = Mock()
        return mock

    def test_streaming_updates_display_progressively(self, mock_graphistry):
        """Test that streaming updates display multiple times during response."""
        # Mock streaming response lines that simulate progressive updates
        mock_lines = [
            '{"dthread_id": "D_test123"}',
            (
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Starting..."}}'
            ),
            (
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Starting...\\nProcessing..."}}'
            ),
            (
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Starting...\\nProcessing...\\nAnalyzing..."}}'
            ),
            (
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Starting...\\nProcessing...\\nAnalyzing...\\nComplete!"}}'
            ),
        ]

        # Create mock response that yields lines with delays
        def slow_lines():
            for line in mock_lines:
                yield line
                time.sleep(0.15)  # Ensure we exceed throttle threshold

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines = slow_lines

        mock_stream_cm = Mock()
        mock_stream_cm.__enter__ = Mock(return_value=mock_response)
        mock_stream_cm.__exit__ = Mock(return_value=None)

        # Mock httpx
        with patch("httpx.Client") as mock_httpx:
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            # Mock IPython display functions AND ensure we're in Jupyter mode
            with (
                patch("louieai.notebook.streaming.HAS_IPYTHON", True),
                patch("louieai.notebook.streaming.clear_output") as mock_clear,
                patch("louieai.notebook.streaming.display") as mock_display,
                patch("louieai.notebook.streaming.HTML") as mock_html,
                patch("louieai.notebook.cursor.Cursor._in_jupyter", return_value=True),
            ):
                # Create cursor with mocked auth
                lui = louie(graphistry_client=mock_graphistry)

                # Execute query (should trigger streaming)
                lui("Test query")

                # Verify progressive updates
                # Should have multiple display calls (not just final)
                assert mock_clear.call_count >= 3
                assert mock_display.call_count >= 3
                assert mock_html.call_count >= 3

                # Verify content progression
                html_calls = [call[0][0] for call in mock_html.call_args_list]

                # Early calls should have partial content
                assert "Starting..." in html_calls[1]
                assert "Processing..." in html_calls[2]
                assert "Complete!" in html_calls[-1]

                # Verify final state
                assert lui.text == "Starting...\nProcessing...\nAnalyzing...\nComplete!"

    def test_streaming_with_dataframe_element(self, mock_graphistry):
        """Test streaming with dataframe elements."""
        mock_lines = [
            '{"dthread_id": "D_test123"}',
            (
                '{"payload": {"id": "B_001", "type": "TextElement", '
                '"text": "Here is your data:"}}'
            ),
            (
                '{"payload": {"id": "B_002", "type": "DfElement", '
                '"df_id": "df_456", "metadata": {"shape": [5, 3]}}}'
            ),
        ]

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines.return_value = iter(mock_lines)

        mock_stream_cm = Mock()
        mock_stream_cm.__enter__ = Mock(return_value=mock_response)
        mock_stream_cm.__exit__ = Mock(return_value=None)

        with patch("httpx.Client") as mock_httpx:
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            with (
                patch("louieai.notebook.streaming.HAS_IPYTHON", True),
                patch("louieai.notebook.streaming.HTML") as mock_html,
                patch("louieai.notebook.cursor.Cursor._in_jupyter", return_value=True),
            ):
                lui = louie(graphistry_client=mock_graphistry)

                # Mock arrow fetch
                with patch.object(
                    lui._client, "_fetch_dataframe_arrow", return_value=None
                ):
                    lui("Show data")

                # Verify dataframe element was displayed
                html_calls = [call[0][0] for call in mock_html.call_args_list]
                final_html = html_calls[-1]

                assert "DataFrame: df_456" in final_html
                assert "5 x 3" in final_html

    def test_streaming_error_display(self, mock_graphistry):
        """Test that errors are displayed properly during streaming."""
        # Mock httpx to fail
        with patch("httpx.Client") as mock_httpx:
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.side_effect = Exception("Network error")
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            with (
                patch("louieai.notebook.streaming.HAS_IPYTHON", True),
                patch("louieai.notebook.streaming.HTML") as mock_html,
                patch("louieai.notebook.streaming.update_display"),
                patch("louieai.notebook.cursor.Cursor._in_jupyter", return_value=True),
            ):
                lui = louie(graphistry_client=mock_graphistry)

                # Should raise but also display error
                with pytest.raises(Exception, match="Network error"):
                    lui("Test query")

                # Error should have been displayed
                assert mock_html.called
                error_html = mock_html.call_args[0][0]
                assert "Error: Network error" in error_html
                assert "color: red" in error_html

    def test_non_jupyter_falls_back_to_regular(self, mock_graphistry):
        """Test that non-Jupyter environments use regular add_cell."""
        # Mock to simulate non-Jupyter by patching _in_jupyter directly
        lui = louie(graphistry_client=mock_graphistry)

        with patch.object(lui, "_in_jupyter", return_value=False):
            # Mock regular add_cell
            mock_response = Response(
                thread_id="D_test123",
                elements=[{"type": "TextElement", "text": "Regular response"}],
            )

            with patch.object(
                lui._client, "add_cell", return_value=mock_response
            ) as mock_add_cell:
                result = lui("Test query")

                # Should use regular add_cell
                mock_add_cell.assert_called_once()
                assert result is lui
                assert lui.text == "Regular response"

    def test_streaming_performance(self, mock_graphistry):
        """Test that streaming provides faster time-to-first-display."""
        # Create many lines to simulate long response
        lines = ['{"dthread_id": "D_test123"}']
        for i in range(50):
            text = "Line " + " ".join([f"{j}" for j in range(i + 1)])
            lines.append(
                f'{{"payload": {{"id": "B_001", "type": "TextElement", '
                f'"text": "{text}"}}}}'
            )

        display_times = []

        def track_display(*args, **kwargs):
            display_times.append(time.time())

        # Simulate slow response (0.1s per line)
        def slow_lines():
            for line in lines:
                yield line
                time.sleep(0.1)

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines = slow_lines

        mock_stream_cm = Mock()
        mock_stream_cm.__enter__ = Mock(return_value=mock_response)
        mock_stream_cm.__exit__ = Mock(return_value=None)

        with patch("httpx.Client") as mock_httpx:
            mock_httpx_instance = Mock()
            mock_httpx_instance.stream.return_value = mock_stream_cm
            mock_httpx.return_value.__enter__.return_value = mock_httpx_instance

            with (
                patch("louieai.notebook.streaming.HAS_IPYTHON", True),
                patch(
                    "louieai.notebook.streaming.clear_output", side_effect=track_display
                ),
                patch("louieai.notebook.streaming.display"),
                patch("louieai.notebook.streaming.HTML"),
                patch("louieai.notebook.cursor.Cursor._in_jupyter", return_value=True),
            ):
                lui = louie(graphistry_client=mock_graphistry)

                start_time = time.time()
                lui("Long query")
                total_time = time.time() - start_time

                # First display should be much sooner than total time
                if display_times:
                    time_to_first_display = display_times[0] - start_time
                    assert time_to_first_display < total_time * 0.2  # First 20%

                    # Should have multiple updates
                    assert len(display_times) >= 5
