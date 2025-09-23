"""Additional edge case tests to improve upload functionality coverage."""

import io
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from louieai._client import LouieClient, Response
from louieai._upload import UploadClient


class TestUploadErrorHandling:
    """Test error handling and edge cases."""

    def test_serialize_dataframe_invalid_format(self):
        """Test error handling for invalid DataFrame format."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        with pytest.raises(ValueError, match="Unsupported format"):
            upload_client._serialize_dataframe(df, "invalid_format")

    def test_serialize_dataframe_all_formats(self):
        """Test DataFrame serialization for all supported formats."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3], "text": ["a", "b", "c"]})

        # Test parquet
        data, filename, content_type = upload_client._serialize_dataframe(df, "parquet")
        assert filename == "data.parquet"
        assert content_type == "application/octet-stream"
        assert len(data) > 0

        # Test CSV
        data, filename, content_type = upload_client._serialize_dataframe(df, "csv")
        assert filename == "data.csv"
        assert content_type == "text/csv"
        assert b"col,text" in data

        # Test JSON
        data, filename, content_type = upload_client._serialize_dataframe(df, "json")
        assert filename == "data.jsonl"
        assert content_type == "application/x-ndjson"
        assert b'"col":1' in data

    def test_serialize_dataframe_arrow_format(self):
        """Test DataFrame serialization with Arrow format."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)
        df = pd.DataFrame({"col": [1, 2, 3]})

        data, filename, content_type = upload_client._serialize_dataframe(df, "arrow")
        assert filename == "data.arrow"
        assert content_type == "application/octet-stream"
        assert len(data) > 0

    def test_get_default_parsing_options_all_formats(self):
        """Test default parsing options for all formats."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # CSV options
        options = upload_client._get_default_parsing_options("csv")
        assert options["type"] == "CSVParsingOptions"
        assert options["header"] == "infer"
        assert options["sep"] == ","

        # JSON options
        options = upload_client._get_default_parsing_options("json")
        assert options["type"] == "JSONParsingOptions"
        assert options["lines"] is True
        assert options["orient"] == "records"

        # Parquet options
        options = upload_client._get_default_parsing_options("parquet")
        assert options["type"] == "ParquetParsingOptions"
        assert options["use_pandas_metadata"] is True

        # Arrow options
        options = upload_client._get_default_parsing_options("arrow")
        assert options["type"] == "ArrowParsingOptions"
        assert options["use_threads"] is True

        # Unknown format
        options = upload_client._get_default_parsing_options("unknown")
        assert options is None


class TestImageSerializationCoverage:
    """Test image serialization edge cases."""

    def test_serialize_image_path_object(self):
        """Test image serialization with Path object."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch(
                "builtins.open",
                lambda *args, **kwargs: io.BytesIO(b"\\x89PNG\\r\\n\\x1a\\n"),
            ),
            patch("mimetypes.guess_type", return_value=("image/png", None)),
        ):
            path_obj = Path("test.png")
            __data, filename, content_type = upload_client._serialize_image(path_obj)
            assert filename == "test.png"
            assert content_type == "image/png"

    def test_serialize_image_svg_detection(self):
        """Test SVG image format detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        svg_content = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", lambda *args, **kwargs: io.BytesIO(svg_content)),
            patch("mimetypes.guess_type", return_value=("image/svg+xml", None)),
        ):
            _data, filename, content_type = upload_client._serialize_image("test.svg")
            assert filename == "test.svg"
            assert content_type == "image/svg+xml"

    def test_serialize_image_unsupported_type(self):
        """Test error handling for unsupported image types."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test unsupported type (not string, bytes, file-like, or PIL Image)
        with pytest.raises(TypeError, match="Unsupported image type"):
            upload_client._serialize_image(123)  # Pass invalid type


class TestBinarySerializationCoverage:
    """Test binary file serialization edge cases."""

    def test_serialize_binary_path_object(self):
        """Test binary serialization with Path object."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch(
                "builtins.open",
                lambda *args, **kwargs: io.BytesIO(b"%PDF-1.4\\ncontent"),
            ),
            patch("mimetypes.guess_type", return_value=("application/pdf", None)),
        ):
            path_obj = Path("test.pdf")
            _data, filename, content_type = upload_client._serialize_binary(path_obj)
            assert filename == "test.pdf"
            assert content_type == "application/pdf"

    def test_serialize_binary_various_office_formats(self):
        """Test detection of various Office document formats."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        # Test Word document detection
        word_signature = b"PK\x03\x04" + b"word/document.xml" + b"\x00" * 980
        _data, filename, content_type = upload_client._serialize_binary(word_signature)
        assert "wordprocessingml" in content_type
        assert filename == "document.docx"

        # Test PowerPoint detection
        ppt_signature = b"PK\x03\x04" + b"ppt/slides/" + b"\x00" * 980
        _data, filename, content_type = upload_client._serialize_binary(ppt_signature)
        assert "presentationml" in content_type
        assert filename == "presentation.pptx"

    def test_serialize_binary_with_custom_filename_override(self):
        """Test that custom filename overrides detection."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        pdf_bytes = b"%PDF-1.4\\ncontent"
        _data, filename, content_type = upload_client._serialize_binary(
            pdf_bytes, filename="custom_name.pdf"
        )
        assert filename == "custom_name.pdf"
        assert content_type == "application/pdf"

    def test_serialize_binary_unsupported_type(self):
        """Test error handling for unsupported binary file types."""
        mock_client = Mock()
        upload_client = UploadClient(mock_client)

        with pytest.raises(TypeError, match="Unsupported file type"):
            upload_client._serialize_binary(123)  # Invalid type


class TestLouieClientMethods:
    """Test LouieClient upload method integration."""

    def test_client_upload_dataframe_method_delegation(self):
        """Test that LouieClient.upload_dataframe properly delegates to UploadClient."""
        with patch("louieai._upload.UploadClient") as mock_upload_class:
            mock_upload_instance = Mock()
            mock_response = Response("test-thread", [])
            mock_upload_instance.upload_dataframe.return_value = mock_response
            mock_upload_class.return_value = mock_upload_instance

            client = LouieClient(server_url="https://test.louie.ai")
            df = pd.DataFrame({"col": [1, 2, 3]})

            result = client.upload_dataframe(
                "Test prompt",
                df,
                format="csv",
                agent="CustomAgent",
                traces=True,
                share_mode="Public",
                name="Custom Name",
                parsing_options={"delimiter": ";"},
            )

            # Verify delegation
            mock_upload_class.assert_called_once_with(client)
            mock_upload_instance.upload_dataframe.assert_called_once_with(
                prompt="Test prompt",
                df=df,
                thread_id="",  # Default thread_id
                format="csv",
                agent="CustomAgent",
                traces=True,
                share_mode="Public",
                name="Custom Name",
                parsing_options={"delimiter": ";"},
            )
            assert result == mock_response

    def test_client_upload_methods_with_thread_id(self):
        """Test client upload methods with thread_id parameter."""
        with patch("louieai._upload.UploadClient") as mock_upload_class:
            mock_upload_instance = Mock()
            mock_response = Response("existing-thread", [])
            mock_upload_instance.upload_image.return_value = mock_response
            mock_upload_instance.upload_binary.return_value = mock_response
            mock_upload_class.return_value = mock_upload_instance

            client = LouieClient(server_url="https://test.louie.ai")

            # Test image upload with thread_id
            client.upload_image("Test", "image.jpg", thread_id="existing-thread")
            mock_upload_instance.upload_image.assert_called_with(
                prompt="Test",
                image="image.jpg",
                thread_id="existing-thread",
                agent="UploadPassthroughAgent",
                traces=False,
                share_mode="Private",
                name=None,
            )

            # Test binary upload with thread_id
            client.upload_binary("Test", "file.pdf", thread_id="existing-thread")
            mock_upload_instance.upload_binary.assert_called_with(
                prompt="Test",
                file="file.pdf",
                thread_id="existing-thread",
                agent="UploadPassthroughAgent",
                traces=False,
                share_mode="Private",
                name=None,
                filename=None,
            )
