"""Additional tests to improve coverage for upload functionality."""

import io
from unittest.mock import Mock, patch

import httpx
import pandas as pd
import pytest

from louieai._client import Response
from louieai._upload import UploadClient


class TestUploadClientCoverage:
    """Additional tests to improve upload client coverage."""

    def test_upload_dataframe_with_all_optional_params(self):
        """Test upload with all optional parameters."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [{"type": "TextElement", "content": "Analysis complete"}],
        }

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as mock_httpx:
            # Setup mock streaming response
            mock_stream_client = Mock()
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines.return_value = iter(
                ['{"type": "TextElement", "content": "Processing..."}']
            )

            mock_stream_context = Mock()
            mock_stream_context.__enter__ = Mock(return_value=mock_response)
            mock_stream_context.__exit__ = Mock(return_value=None)
            mock_stream_client.stream.return_value = mock_stream_context

            mock_httpx.return_value = mock_stream_client

            # Test with all optional parameters
            result = upload_client.upload_dataframe(
                prompt="Analyze this data",
                df=df,
                thread_id="existing-thread-123",
                format="json",
                agent="UploadAgent",
                traces=True,
                share_mode="Organization",
                name="Custom Analysis",
                parsing_options={"lines": True, "orient": "records"},
            )

            assert isinstance(result, Response)

    def test_upload_dataframe_with_default_parsing_options(self):
        """Test upload with default parsing options for different formats."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [],
        }

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        # Test different formats to trigger default parsing options
        formats_to_test = ["csv", "json", "parquet", "arrow"]

        for fmt in formats_to_test:
            with patch("httpx.Client") as mock_httpx:
                mock_stream_client = self._setup_mock_stream_client(["{}"])
                mock_httpx.return_value = mock_stream_client

                result = upload_client.upload_dataframe(
                    prompt="Test", df=df, format=fmt
                )
                assert isinstance(result, Response)

    def test_upload_dataframe_error_handling_edge_case(self):
        """Test edge case error handling in dataframe upload."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [],
        }

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as mock_httpx:
            mock_stream_client = Mock()
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines.return_value = iter(
                ['{"type": "TextElement", "content": "Processing..."}']
            )

            mock_stream_context = Mock()
            mock_stream_context.__enter__ = Mock(return_value=mock_response)
            mock_stream_context.__exit__ = Mock(return_value=None)
            mock_stream_client.stream.return_value = mock_stream_context

            mock_httpx.return_value = mock_stream_client

            # Test with edge case format
            result = upload_client.upload_dataframe("Test", df, format="csv")
            assert isinstance(result, Response)

    def test_upload_dataframe_read_timeout_with_lines(self):
        """Test ReadTimeout exception when lines were received."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [],
        }

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as mock_httpx:
            mock_stream_client = Mock()
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()

            def iter_with_timeout():
                yield '{"type": "TextElement", "content": "Processing..."}'
                raise httpx.ReadTimeout("Timeout")

            mock_response.iter_lines.return_value = iter_with_timeout()

            mock_stream_context = Mock()
            mock_stream_context.__enter__ = Mock(return_value=mock_response)
            mock_stream_context.__exit__ = Mock(return_value=None)
            mock_stream_client.stream.return_value = mock_stream_context

            mock_httpx.return_value = mock_stream_client

            with patch("louieai._upload.logger") as mock_logger:
                result = upload_client.upload_dataframe("Test", df)

                # Should log info about successful partial stream
                mock_logger.info.assert_called()
                assert isinstance(result, Response)

    def test_upload_dataframe_read_timeout_no_lines(self):
        """Test ReadTimeout exception when no lines were received."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as mock_httpx:
            mock_stream_client = Mock()
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines.return_value = iter([])  # No lines
            mock_response.iter_lines.side_effect = httpx.ReadTimeout("Timeout")

            mock_stream_context = Mock()
            mock_stream_context.__enter__ = Mock(return_value=mock_response)
            mock_stream_context.__exit__ = Mock(return_value=None)
            mock_stream_client.stream.return_value = mock_stream_context

            mock_httpx.return_value = mock_stream_client

            # Should raise the timeout exception
            with pytest.raises(httpx.ReadTimeout):
                upload_client.upload_dataframe("Test", df)

    def test_upload_dataframe_with_dataframe_fetching(self):
        """Test dataframe fetching from response."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30

        # Mock response with dataframes to fetch
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [
                {"type": "DfElement", "id": "df-123", "content": "DataFrame result"},
                {"type": "df", "id": "df-456", "content": "Another DataFrame"},
            ],
        }

        # Mock successful dataframe fetching
        mock_df = pd.DataFrame({"result": [1, 2, 3]})
        mock_client._fetch_dataframe_arrow.return_value = mock_df

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as mock_httpx:
            mock_stream_client = self._setup_mock_stream_client(
                ['{"type": "TextElement", "content": "Analysis complete"}']
            )
            mock_httpx.return_value = mock_stream_client

            result = upload_client.upload_dataframe("Test", df)

            # Should call fetch for both dataframes
            assert mock_client._fetch_dataframe_arrow.call_count == 2

            # Should attach fetched dataframes to elements
            assert result.elements[0]["table"] is mock_df
            assert result.elements[1]["table"] is mock_df

    def test_upload_dataframe_failed_dataframe_fetching(self):
        """Test handling of failed dataframe fetching."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30

        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [
                {"type": "DfElement", "id": "df-123", "content": "DataFrame result"}
            ],
        }

        # Mock failed dataframe fetching
        mock_client._fetch_dataframe_arrow.return_value = None

        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with patch("httpx.Client") as mock_httpx:
            mock_stream_client = self._setup_mock_stream_client(
                ['{"type": "TextElement", "content": "Analysis complete"}']
            )
            mock_httpx.return_value = mock_stream_client

            result = upload_client.upload_dataframe("Test", df)

            # Should try to fetch dataframe
            mock_client._fetch_dataframe_arrow.assert_called_once()

            # Element should not have table key when fetch fails
            assert "table" not in result.elements[0]

    def test_serialize_image_file_like_with_name(self):
        """Test image serialization from file-like object with name."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create BytesIO with PNG data and name
        img_data = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"fake_png_data")
        img_data.name = "/path/to/test.png"

        file_data, filename, content_type = upload_client._serialize_image(img_data)

        assert filename == "test.png"
        assert content_type == "image/png"
        assert file_data == b"\x89PNG\r\n\x1a\n" + b"fake_png_data"

    def test_serialize_image_file_like_content_detection(self):
        """Test image serialization with content-based detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create file-like object with JPEG signature
        img_data = io.BytesIO(b"\xff\xd8\xff\xe0" + b"jpeg_data")
        # Set name to something that mimetypes can't guess
        img_data.name = "unknown"

        with patch("mimetypes.guess_type", return_value=(None, None)):
            _file_data, filename, content_type = upload_client._serialize_image(
                img_data
            )

        # Should detect JPEG from content and set appropriate filename
        assert filename == "image.jpg"
        assert content_type == "image/jpeg"

    def test_serialize_binary_with_word_document(self):
        """Test binary serialization of Word document."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create Word document signature
        word_content = b"PK\x03\x04" + b"word/document.xml" + b"\x00" * 980

        _file_data, filename, content_type = upload_client._serialize_binary(
            word_content
        )

        assert filename == "document.docx"
        assert "wordprocessingml" in content_type

    def test_serialize_binary_with_powerpoint(self):
        """Test binary serialization of PowerPoint presentation."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create PowerPoint signature
        ppt_content = b"PK\x03\x04" + b"ppt/slides/" + b"\x00" * 980

        _file_data, filename, content_type = upload_client._serialize_binary(
            ppt_content
        )

        assert filename == "presentation.pptx"
        assert "presentationml" in content_type

    def test_serialize_binary_with_zip_file(self):
        """Test binary serialization of generic ZIP file."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create generic ZIP signature
        zip_content = b"PK\x03\x04" + b"some/file.txt" + b"\x00" * 980

        _file_data, filename, content_type = upload_client._serialize_binary(
            zip_content
        )

        assert filename == "archive.zip"
        assert content_type == "application/zip"

    def test_serialize_binary_with_json_content(self):
        """Test binary serialization of JSON content."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # JSON content as bytes
        json_content = b'{"key": "value", "data": [1, 2, 3]}'

        _file_data, filename, content_type = upload_client._serialize_binary(
            json_content
        )

        assert filename == "data.json"
        assert content_type == "application/json"

    def test_serialize_binary_with_json_array(self):
        """Test binary serialization of JSON array."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # JSON array as bytes
        json_content = b'[{"item": 1}, {"item": 2}]'

        _file_data, filename, content_type = upload_client._serialize_binary(
            json_content
        )

        assert filename == "data.json"
        assert content_type == "application/json"

    def test_serialize_binary_file_like_with_pdf_detection(self):
        """Test binary serialization from file-like with PDF detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create BytesIO with PDF signature
        pdf_data = io.BytesIO(b"%PDF-1.4\nfake content")
        pdf_data.name = "unknown"  # Set name that mimetypes can't guess

        with patch("mimetypes.guess_type", return_value=(None, None)):
            _file_data, _filename, content_type = upload_client._serialize_binary(
                pdf_data
            )

        # Should detect PDF from content signature
        assert content_type == "application/pdf"

    def test_serialize_binary_file_like_with_zip_detection(self):
        """Test binary serialization from file-like with ZIP detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create BytesIO with ZIP data
        zip_data = io.BytesIO(b"PK\x03\x04some zip data")
        zip_data.name = "archive.unknown"

        _file_data, _filename, content_type = upload_client._serialize_binary(zip_data)

        assert content_type == "application/zip"

    def _setup_mock_stream_client(self, response_lines):
        """Helper to setup mock streaming client."""
        mock_stream_client = Mock()
        mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
        mock_stream_client.__exit__ = Mock(return_value=None)

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines.return_value = iter(response_lines)

        mock_stream_context = Mock()
        mock_stream_context.__enter__ = Mock(return_value=mock_response)
        mock_stream_context.__exit__ = Mock(return_value=None)
        mock_stream_client.stream.return_value = mock_stream_context

        return mock_stream_client


class TestImageUploadCoverage:
    """Additional tests for image upload coverage."""

    def test_upload_image_with_all_params(self):
        """Test image upload with all optional parameters."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [],
        }

        upload_client = UploadClient(mock_client)

        with patch("httpx.Client") as mock_httpx:
            mock_stream_client = Mock()
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines.return_value = iter(
                ['{"type": "TextElement", "content": "Image analyzed"}']
            )

            mock_stream_context = Mock()
            mock_stream_context.__enter__ = Mock(return_value=mock_response)
            mock_stream_context.__exit__ = Mock(return_value=None)
            mock_stream_client.stream.return_value = mock_stream_context

            mock_httpx.return_value = mock_stream_client

            png_bytes = b"\x89PNG\r\n\x1a\n"
            result = upload_client.upload_image(
                prompt="Analyze image",
                image=png_bytes,
                thread_id="existing-thread",
                agent="UploadAgent",
                traces=True,
                share_mode="Public",
                name="Image Analysis",
            )

            assert isinstance(result, Response)


class TestBinaryUploadCoverage:
    """Additional tests for binary upload coverage."""

    def test_upload_binary_with_all_params(self):
        """Test binary upload with all optional parameters."""
        mock_client = Mock()
        mock_client._get_headers.return_value = {"Authorization": "Bearer token"}
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 60
        mock_client._streaming_timeout = 30
        mock_client._parse_jsonl_response.return_value = {
            "dthread_id": "test-thread-123",
            "elements": [],
        }

        upload_client = UploadClient(mock_client)

        with patch("httpx.Client") as mock_httpx:
            mock_stream_client = Mock()
            mock_stream_client.__enter__ = Mock(return_value=mock_stream_client)
            mock_stream_client.__exit__ = Mock(return_value=None)

            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.iter_lines.return_value = iter(
                ['{"type": "TextElement", "content": "File analyzed"}']
            )

            mock_stream_context = Mock()
            mock_stream_context.__enter__ = Mock(return_value=mock_response)
            mock_stream_context.__exit__ = Mock(return_value=None)
            mock_stream_client.stream.return_value = mock_stream_context

            mock_httpx.return_value = mock_stream_client

            pdf_bytes = b"%PDF-1.4\ncontent"
            result = upload_client.upload_binary(
                prompt="Analyze file",
                file=pdf_bytes,
                thread_id="existing-thread",
                agent="UploadAgent",
                traces=True,
                share_mode="Organization",
                name="File Analysis",
                filename="custom.pdf",
            )

            assert isinstance(result, Response)

    def test_serialize_binary_with_custom_filename(self):
        """Test binary serialization with custom filename."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test with custom filename overriding detection
        pdf_bytes = b"%PDF-1.4\ncontent"
        _file_data, filename, content_type = upload_client._serialize_binary(
            pdf_bytes, filename="custom.pdf"
        )

        assert filename == "custom.pdf"
        assert content_type == "application/pdf"

    def test_serialize_binary_file_like_with_custom_filename(self):
        """Test binary serialization from file-like with custom filename."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Create file-like object
        file_obj = io.BytesIO(b"some binary data")
        file_obj.name = "original.bin"

        _file_data, filename, _content_type = upload_client._serialize_binary(
            file_obj, filename="override.txt"
        )

        assert filename == "override.txt"


class TestImageFormats:
    """Test various image format detections."""

    def test_gif_detection(self):
        """Test GIF format detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        gif_bytes = b"GIF87a" + b"fake gif data"
        _file_data, filename, content_type = upload_client._serialize_image(gif_bytes)

        assert filename == "image.gif"
        assert content_type == "image/gif"

    def test_bmp_detection(self):
        """Test BMP format detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        bmp_bytes = b"BM" + b"fake bmp data"
        _file_data, filename, content_type = upload_client._serialize_image(bmp_bytes)

        assert filename == "image.bmp"
        assert content_type == "image/bmp"

    def test_webp_detection(self):
        """Test WebP format detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        webp_bytes = b"RIFF" + b"1234WEBP" + b"fake webp data"
        _file_data, filename, content_type = upload_client._serialize_image(webp_bytes)

        assert filename == "image.webp"
        assert content_type == "image/webp"

    def test_get_default_parsing_options(self):
        """Test default parsing options."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test CSV options
        options = upload_client._get_default_parsing_options("csv")
        assert options["type"] == "CSVParsingOptions"
        assert options["header"] == "infer"

        # Test JSON options
        options = upload_client._get_default_parsing_options("json")
        assert options["type"] == "JSONParsingOptions"
        assert options["lines"] is True

        # Test parquet options
        options = upload_client._get_default_parsing_options("parquet")
        assert options["type"] == "ParquetParsingOptions"

        # Test arrow options
        options = upload_client._get_default_parsing_options("arrow")
        assert options["type"] == "ArrowParsingOptions"

        # Test unknown format returns None
        options = upload_client._get_default_parsing_options("unknown")
        assert options is None

    def test_unknown_image_format(self):
        """Test unknown image format fallback."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        unknown_bytes = b"UNKNOWN_FORMAT"
        _file_data, filename, content_type = upload_client._serialize_image(
            unknown_bytes
        )

        assert filename == "image.bin"
        assert content_type == "application/octet-stream"
