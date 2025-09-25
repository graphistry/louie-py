"""Simple timeout tests for upload module."""

from unittest.mock import Mock, patch

import httpx
import pandas as pd

from louieai._upload import UploadClient


class TestUploadTimeout:
    """Test timeout handling in upload operations."""

    def test_upload_dataframe_read_timeout_with_partial_data(self):
        """Test handling of ReadTimeout after receiving some data."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_123", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            # Mock response that yields some data then raises ReadTimeout
            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            lines = ['{"dthread_id": "D_123"}', '{"payload": {"type": "text"}}']

            def iter_lines():
                yield from lines
                raise httpx.ReadTimeout("Timeout")

            mock_response.iter_lines = iter_lines

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            # Should handle timeout gracefully since we got some data
            with (
                patch("louieai._upload.logger") as mock_logger,
                patch("time.time", return_value=100),
            ):
                response = upload_client.upload_dataframe("test", df)

                # Should have logged info about partial response
                mock_logger.info.assert_called()
                assert "Stream ended" in str(mock_logger.info.call_args)
                assert response.thread_id == "D_123"

    def test_upload_dataframe_read_timeout_no_data(self):
        """Test handling of ReadTimeout with no data received."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            # Mock response that immediately raises ReadTimeout
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(side_effect=httpx.ReadTimeout("Timeout"))

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            # Should re-raise timeout when no data received
            import pytest

            with pytest.raises(httpx.ReadTimeout):
                upload_client.upload_dataframe("test", df)

    def test_upload_image_timeout_with_data(self):
        """Test image upload timeout after partial data."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_img", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        image = b"\x89PNG\r\n\x1a\n" + b"data"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            def iter_lines():
                yield '{"dthread_id": "D_img"}'
                raise httpx.ReadTimeout("Timeout")

            mock_response.iter_lines = iter_lines

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            with (
                patch("louieai._upload.logger") as mock_logger,
                patch("time.time", return_value=100),
            ):
                response = upload_client.upload_image("test", image)

                mock_logger.info.assert_called()
                assert response.thread_id == "D_img"

    def test_upload_dataframe_with_dataframe_element(self):
        """Test handling of dataframe elements in response."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={
                "dthread_id": "D_df",
                "elements": [{"type": "DfElement", "id": "df_001"}],
            }
        )
        mock_client._fetch_dataframe_arrow = Mock(
            return_value=pd.DataFrame({"result": [1, 2]})
        )

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(
                return_value=[
                    '{"dthread_id": "D_df"}',
                    '{"elements": [{"type": "DfElement", "id": "df_001"}]}',
                ]
            )

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            with patch("time.time", return_value=100):
                response = upload_client.upload_dataframe("test", df)

                # Should have fetched the dataframe
                mock_client._fetch_dataframe_arrow.assert_called_with("D_df", "df_001")
                assert response.thread_id == "D_df"

    def test_upload_binary_timeout_no_data(self):
        """Test binary upload timeout with no data."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1

        upload_client = UploadClient(mock_client)
        pdf = b"%PDF-1.4\n" + b"content"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(side_effect=httpx.ReadTimeout("Timeout"))

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            import pytest

            with pytest.raises(httpx.ReadTimeout):
                upload_client.upload_binary("test", pdf)

    def test_upload_image_timeout_triggers_warning(self):
        """Test image upload timeout triggers streaming warning."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 0.5
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_img_warn", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        image = b"\x89PNG\r\n\x1a\n" + b"data"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            def iter_lines():
                yield '{"dthread_id": "D_img_warn"}'
                # Stop yielding to trigger timeout
                return

            mock_response.iter_lines = iter_lines

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            # Mock time to trigger timeout warning
            with (
                patch("time.time", side_effect=[0, 0.1, 2.0]),
                patch("louieai._upload.logger") as mock_logger,
            ):
                response = upload_client.upload_image("test", image)

                mock_logger.warning.assert_called()
                assert "Streaming timeout" in str(mock_logger.warning.call_args)
                assert response.thread_id == "D_img_warn"

    def test_upload_binary_timeout_triggers_warning(self):
        """Test binary upload timeout triggers streaming warning."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 0.5
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_bin_warn", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        pdf = b"%PDF-1.4\n" + b"content"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            def iter_lines():
                yield '{"dthread_id": "D_bin_warn"}'
                return

            mock_response.iter_lines = iter_lines

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            with (
                patch("time.time", side_effect=[0, 0.1, 2.0]),
                patch("louieai._upload.logger") as mock_logger,
            ):
                response = upload_client.upload_binary("test", pdf)

                mock_logger.warning.assert_called()
                assert response.thread_id == "D_bin_warn"

    def test_upload_image_with_dataframe_element(self):
        """Test image upload with dataframe element in response."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={
                "dthread_id": "D_img_df",
                "elements": [{"type": "df", "id": "df_002"}],
            }
        )
        mock_client._fetch_dataframe_arrow = Mock(
            return_value=pd.DataFrame({"img_result": [1]})
        )

        upload_client = UploadClient(mock_client)
        image = b"\x89PNG\r\n\x1a\n" + b"data"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(return_value=['{"dthread_id": "D_img_df"}'])

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            with patch("time.time", return_value=100):
                response = upload_client.upload_image("test", image)

                mock_client._fetch_dataframe_arrow.assert_called_with(
                    "D_img_df", "df_002"
                )
                assert response.thread_id == "D_img_df"

    def test_upload_binary_with_dataframe_element(self):
        """Test binary upload with dataframe element in response."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 1
        mock_client._parse_jsonl_response = Mock(
            return_value={
                "dthread_id": "D_bin_df",
                "elements": [{"type": "DfElement", "id": "df_003"}],
            }
        )
        mock_client._fetch_dataframe_arrow = Mock(
            return_value=pd.DataFrame({"bin_result": [1]})
        )

        upload_client = UploadClient(mock_client)
        pdf = b"%PDF-1.4\n" + b"content"

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines = Mock(return_value=['{"dthread_id": "D_bin_df"}'])

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            with patch("time.time", return_value=100):
                response = upload_client.upload_binary("test", pdf)

                mock_client._fetch_dataframe_arrow.assert_called_with(
                    "D_bin_df", "df_003"
                )
                assert response.thread_id == "D_bin_df"

    def test_upload_streaming_timeout_detection(self):
        """Test detection of streaming timeout during upload."""
        mock_client = Mock()
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 10
        mock_client._streaming_timeout = 0.5  # Short timeout for testing
        mock_client._parse_jsonl_response = Mock(
            return_value={"dthread_id": "D_stream", "elements": []}
        )

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as MockClient:
            mock_stream_client = MockClient.return_value
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            # Create an iterator that actually triggers timeout
            lines_yielded = []

            def slow_iter():
                lines_yielded.append('{"dthread_id": "D_stream"}')
                yield lines_yielded[-1]
                # After first line, we'll exceed timeout
                return

            mock_response.iter_lines = slow_iter

            mock_stream_client.stream.return_value.__enter__ = Mock(
                return_value=mock_response
            )
            mock_stream_client.stream.return_value.__exit__ = Mock(return_value=None)

            # Mock time to simulate timeout: initial, after first line, way later
            time_values = [0, 0.1, 2.0]  # Last value exceeds streaming_timeout
            with (
                patch("time.time", side_effect=time_values),
                patch("louieai._upload.logger") as mock_logger,
            ):
                response = upload_client.upload_dataframe("test", df)

                # Should have logged warning about streaming timeout
                mock_logger.warning.assert_called()
                warning_msg = str(mock_logger.warning.call_args)
                assert "Streaming timeout" in warning_msg
                assert response.thread_id == "D_stream"
