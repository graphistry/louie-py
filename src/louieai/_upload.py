"""DataFrame upload functionality for Louie.ai."""

import io
import json
import logging
import mimetypes
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO

if TYPE_CHECKING:
    from ._client import Response

import httpx
import pandas as pd

from .auth import auto_retry_auth

logger = logging.getLogger(__name__)


class UploadClient:
    """Handles DataFrame uploads to Louie.ai via the new upload API."""

    def __init__(self, client: Any):
        """Initialize with parent client for auth and settings."""
        self._client = client

    @auto_retry_auth
    def upload_dataframe(
        self,
        prompt: str,
        df: pd.DataFrame,
        thread_id: str = "",
        *,
        format: str = "parquet",
        agent: str = "UploadPassthroughAgent",
        traces: bool = False,
        share_mode: str = "Private",
        name: str | None = None,
        parsing_options: dict[str, Any] | None = None,
    ) -> "Response":
        """Upload a DataFrame with a natural language query for analysis.

        This method uploads a pandas DataFrame to Louie.ai along with a prompt,
        enabling AI-powered data analysis. The DataFrame is serialized to the
        specified format and sent via multipart upload.

        Args:
            prompt: Natural language query about the data (e.g., "Summarize trends",
                "Find anomalies", "Calculate statistics")
            df: Pandas DataFrame to analyze
            thread_id: Thread ID to continue conversation (empty string creates
                new thread)
            format: Serialization format - "parquet" (recommended), "csv", "json",
                "jsonl", or "arrow". Parquet is fastest and preserves data types best.
            agent: AI agent to use. "UploadPassthroughAgent" (default) automatically
                parses data without LLM. "UploadAgent" uses LLM for parsing.
            traces: Whether to include reasoning traces in response (default: False)
            share_mode: Visibility - "Private" (default), "Organization", or "Public"
            name: Optional thread name (auto-generated from prompt if not provided)
            parsing_options: Dict of format-specific parsing options (e.g., for CSV:
                {"delimiter": ",", "header": true}). If None, uses sensible defaults.

        Returns:
            Response object containing:
                - thread_id: Conversation thread identifier
                - elements: List of response elements (text, dataframes, graphs, etc.)
                - text: Primary text response
                - df/dfs: Any returned DataFrames

        Examples:
            Basic usage:
            >>> df = pd.DataFrame({"sales": [100, 200, 150], "month": [1, 2, 3]})
            >>> response = client.upload_dataframe("What's the trend?", df)
            >>> print(response.text)

            With CSV format and parsing options:
            >>> response = client.upload_dataframe(
            ...     "Analyze this data",
            ...     df,
            ...     format="csv",
            ...     parsing_options={"delimiter": ",", "index": False}
            ... )

            Continue conversation in same thread:
            >>> response2 = client.upload_dataframe(
            ...     "Now show monthly averages",
            ...     df,
            ...     thread_id=response.thread_id
            ... )
        """
        # Get headers with auth
        headers = self._client._get_headers()

        # Serialize DataFrame to specified format
        file_data, filename, content_type = self._serialize_dataframe(df, format)

        # Prepare form data
        files = [("files", (filename, file_data, content_type))]

        data = {
            "query": prompt,
            "agent": agent,
            "ignore_traces": str(not traces).lower(),
            "share_mode": share_mode,
        }

        # Add optional fields
        if thread_id:
            data["dthread_id"] = thread_id
        if name:
            data["name"] = name

        # Add parsing options if provided
        if parsing_options:
            # For single file, wrap in array
            data["parsing_options"] = json.dumps([parsing_options])
        else:
            # Use default parsing options based on format
            default_options = self._get_default_parsing_options(format)
            if default_options:
                data["parsing_options"] = json.dumps([default_options])

        # Make upload request with streaming response
        response_text = ""
        lines_received = 0
        start_time = time.time()

        # Use configured timeouts
        stream_client = httpx.Client(
            timeout=httpx.Timeout(
                self._client._timeout,  # Overall timeout
                read=self._client._streaming_timeout,  # Per-chunk timeout
            )
        )

        with (
            stream_client,
            stream_client.stream(
                "POST",
                f"{self._client.server_url}/api/chat_upload/",
                headers=headers,
                data=data,
                files=files,
            ) as response,
        ):
            response.raise_for_status()

            # Collect streaming lines
            last_activity = start_time
            try:
                for line in response.iter_lines():
                    if line:
                        response_text += line + "\n"
                        lines_received += 1
                        last_activity = time.time()

                    # Check for timeout
                    time_since_activity = time.time() - last_activity
                    if time_since_activity > self._client._streaming_timeout:
                        logger.warning(
                            f"Streaming timeout after {time_since_activity:.1f}s "
                            f"of inactivity. Received {lines_received} lines."
                        )
                        break

            except httpx.ReadTimeout:
                elapsed = time.time() - start_time
                if lines_received > 0:
                    logger.info(
                        f"Stream ended after {elapsed:.1f}s with {lines_received} lines"
                    )
                else:
                    raise

        # Parse response and create Response object
        parsed = self._client._parse_jsonl_response(response_text)

        # Fetch any dataframes that were returned
        if parsed.get("dthread_id"):
            for elem in parsed.get("elements", []):
                if elem.get("type") in ["DfElement", "df"] and elem.get("id"):
                    # Fetch the actual dataframe
                    fetched_df = self._client._fetch_dataframe_arrow(
                        parsed["dthread_id"], elem["id"]
                    )
                    if fetched_df is not None:
                        elem["table"] = fetched_df

        from ._client import Response

        return Response(
            thread_id=parsed.get("dthread_id", ""), elements=parsed.get("elements", [])
        )

    def _serialize_dataframe(
        self, df: pd.DataFrame, format: str
    ) -> tuple[bytes, str, str]:
        """Serialize DataFrame to specified format.

        Args:
            df: DataFrame to serialize
            format: Target format (parquet, csv, json, arrow)

        Returns:
            Tuple of (file_data, filename, content_type)
        """
        buffer = io.BytesIO()

        if format == "parquet":
            df.to_parquet(buffer, index=False, engine="pyarrow")
            filename = "data.parquet"
            content_type = "application/octet-stream"
        elif format == "csv":
            df.to_csv(buffer, index=False)
            filename = "data.csv"
            content_type = "text/csv"
        elif format in ["json", "jsonl"]:
            df.to_json(buffer, orient="records", lines=True)
            filename = "data.jsonl"
            content_type = "application/x-ndjson"
        elif format == "arrow":
            import pyarrow as pa
            import pyarrow.ipc as ipc

            table = pa.Table.from_pandas(df)
            with ipc.new_file(buffer, table.schema) as writer:
                writer.write_table(table)
            filename = "data.arrow"
            content_type = "application/octet-stream"
        else:
            raise ValueError(
                f"Unsupported format: {format}. "
                f"Use 'parquet', 'csv', 'json', 'jsonl', or 'arrow'"
            )

        buffer.seek(0)
        return buffer.read(), filename, content_type

    def _get_default_parsing_options(self, format: str) -> dict[str, Any] | None:
        """Get default parsing options for format.

        Args:
            format: File format

        Returns:
            Default parsing options or None
        """
        options_map: dict[str, dict[str, Any]] = {
            "csv": {
                "type": "CSVParsingOptions",
                "header": "infer",
                "sep": ",",
            },
            "json": {
                "type": "JSONParsingOptions",
                "lines": True,
                "orient": "records",
            },
            "jsonl": {
                "type": "JSONParsingOptions",
                "lines": True,
                "orient": "records",
            },
            "parquet": {
                "type": "ParquetParsingOptions",
                "use_pandas_metadata": True,
            },
            "arrow": {
                "type": "ArrowParsingOptions",
                "use_threads": True,
            },
        }
        return options_map.get(format)

    @auto_retry_auth
    def upload_image(
        self,
        prompt: str,
        image: str | bytes | BinaryIO | Any,
        thread_id: str = "",
        *,
        agent: str = "UploadPassthroughAgent",
        traces: bool = False,
        share_mode: str = "Private",
        name: str | None = None,
    ) -> "Response":
        """Upload an image with a natural language query for analysis.

        This method uploads an image to Louie.ai for AI-powered visual analysis.
        Supports various image formats and input types.

        Args:
            prompt: Natural language query about the image (e.g.,
                "What's in this image?", "Describe the chart",
                "Extract text from this screenshot")
            image: Image to analyze. Can be:
                - File path (str or Path)
                - Raw bytes
                - File-like object (BytesIO, opened file)
                - PIL Image object
            thread_id: Thread ID to continue conversation (empty string creates
                new thread)
            agent: AI agent to use. "UploadPassthroughAgent" (default) for
                direct analysis
            traces: Whether to include reasoning traces in response (default: False)
            share_mode: Visibility - "Private" (default), "Organization", or "Public"
            name: Optional thread name (auto-generated from prompt if not provided)

        Returns:
            Response object containing AI analysis of the image

        Examples:
            From file path:
            >>> response = client.upload_image("What's in this photo?", "photo.jpg")

            From PIL Image:
            >>> from PIL import Image
            >>> img = Image.open("chart.png")
            >>> response = client.upload_image("Explain this chart", img)

            From bytes:
            >>> with open("screenshot.png", "rb") as f:
            ...     img_bytes = f.read()
            >>> response = client.upload_image("Extract text", img_bytes)
        """
        # Get headers with auth
        headers = self._client._get_headers()

        # Serialize image
        file_data, filename, content_type = self._serialize_image(image)

        # Prepare form data
        files = [("files", (filename, file_data, content_type))]

        data = {
            "query": prompt,
            "agent": agent,
            "ignore_traces": str(not traces).lower(),
            "share_mode": share_mode,
        }

        # Add optional fields
        if thread_id:
            data["dthread_id"] = thread_id
        if name:
            data["name"] = name

        # Make upload request with streaming response
        response_text = ""
        lines_received = 0
        start_time = time.time()

        # Use configured timeouts
        stream_client = httpx.Client(
            timeout=httpx.Timeout(
                self._client._timeout,  # Overall timeout
                read=self._client._streaming_timeout,  # Per-chunk timeout
            )
        )

        with (
            stream_client,
            stream_client.stream(
                "POST",
                f"{self._client.server_url}/api/chat_upload/",
                headers=headers,
                data=data,
                files=files,
            ) as response,
        ):
            response.raise_for_status()

            # Collect streaming lines
            last_activity = start_time
            try:
                for line in response.iter_lines():
                    if line:
                        response_text += line + "\n"
                        lines_received += 1
                        last_activity = time.time()

                    # Check for timeout
                    time_since_activity = time.time() - last_activity
                    if time_since_activity > self._client._streaming_timeout:
                        logger.warning(
                            f"Streaming timeout after {time_since_activity:.1f}s "
                            f"of inactivity. Received {lines_received} lines."
                        )
                        break

            except httpx.ReadTimeout:
                elapsed = time.time() - start_time
                if lines_received > 0:
                    logger.info(
                        f"Stream ended after {elapsed:.1f}s with {lines_received} lines"
                    )
                else:
                    raise

        # Parse response and create Response object
        parsed = self._client._parse_jsonl_response(response_text)

        # Fetch any dataframes that were returned
        if parsed.get("dthread_id"):
            for elem in parsed.get("elements", []):
                if elem.get("type") in ["DfElement", "df"] and elem.get("id"):
                    # Fetch the actual dataframe
                    fetched_df = self._client._fetch_dataframe_arrow(
                        parsed["dthread_id"], elem["id"]
                    )
                    if fetched_df is not None:
                        elem["table"] = fetched_df

        from ._client import Response

        return Response(
            thread_id=parsed.get("dthread_id", ""), elements=parsed.get("elements", [])
        )

    def _serialize_image(
        self,
        image: str | bytes | BinaryIO | Any,
    ) -> tuple[bytes, str, str]:
        """Serialize image to bytes for upload.

        Args:
            image: Image in various formats

        Returns:
            Tuple of (file_data, filename, content_type)
        """
        # Handle file path
        if isinstance(image, str | Path):
            path = Path(image)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")

            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(str(path))
            if not mime_type or not mime_type.startswith("image/"):
                # Try to detect from content
                with open(path, "rb") as f:
                    header = f.read(12)
                    if header.startswith(b"\x89PNG"):
                        mime_type = "image/png"
                    elif header.startswith(b"\xff\xd8\xff"):
                        mime_type = "image/jpeg"
                    elif header.startswith(b"GIF8"):
                        mime_type = "image/gif"
                    elif header.startswith(b"BM"):
                        mime_type = "image/bmp"
                    elif header.startswith(b"RIFF") and b"WEBP" in header:
                        mime_type = "image/webp"
                    else:
                        mime_type = "application/octet-stream"

            with open(path, "rb") as f:
                file_data = f.read()
            filename = path.name
            return file_data, filename, mime_type or "application/octet-stream"

        # Handle bytes
        elif isinstance(image, bytes):
            # Detect format from bytes
            if image.startswith(b"\x89PNG"):
                return image, "image.png", "image/png"
            elif image.startswith(b"\xff\xd8\xff"):
                return image, "image.jpg", "image/jpeg"
            elif image.startswith(b"GIF8"):
                return image, "image.gif", "image/gif"
            elif image.startswith(b"BM"):
                return image, "image.bmp", "image/bmp"
            elif image.startswith(b"RIFF") and b"WEBP" in image[8:12]:
                return image, "image.webp", "image/webp"
            else:
                return image, "image.bin", "application/octet-stream"

        # Handle file-like objects
        elif hasattr(image, "read"):
            file_data = image.read()
            if hasattr(image, "seek"):
                image.seek(0)  # Reset for potential reuse

            # Try to get filename
            filename = getattr(image, "name", "image.bin")
            if isinstance(filename, str):
                filename = os.path.basename(filename)
            else:
                filename = "image.bin"

            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                # Detect from content
                if file_data.startswith(b"\x89PNG"):
                    mime_type = "image/png"
                    filename = "image.png"
                elif file_data.startswith(b"\xff\xd8\xff"):
                    mime_type = "image/jpeg"
                    filename = "image.jpg"
                elif file_data.startswith(b"GIF8"):
                    mime_type = "image/gif"
                    filename = "image.gif"
                else:
                    mime_type = "application/octet-stream"

            return file_data, filename, mime_type

        # Handle PIL Image
        else:
            try:
                from PIL import Image

                if isinstance(image, Image.Image):
                    buffer = io.BytesIO()
                    # Default to PNG for best quality
                    format = image.format or "PNG"
                    if format.upper() == "JPEG":
                        image.save(buffer, format="JPEG", quality=95)
                        filename = "image.jpg"
                        content_type = "image/jpeg"
                    else:
                        image.save(buffer, format="PNG")
                        filename = "image.png"
                        content_type = "image/png"
                    buffer.seek(0)
                    return buffer.read(), filename, content_type
            except ImportError:
                pass

            raise TypeError(
                f"Unsupported image type: {type(image)}. "
                "Expected file path, bytes, file-like object, or PIL Image"
            )

    @auto_retry_auth
    def upload_binary(
        self,
        prompt: str,
        file: str | bytes | BinaryIO,
        thread_id: str = "",
        *,
        agent: str = "UploadPassthroughAgent",
        traces: bool = False,
        share_mode: str = "Private",
        name: str | None = None,
        filename: str | None = None,
    ) -> "Response":
        """Upload a binary file with a natural language query for analysis.

        This method uploads any type of file to Louie.ai for AI-powered analysis.
        Supports PDFs, Excel files, Word documents, and any other binary format.

        Args:
            prompt: Natural language query about the file (e.g.,
                "Summarize this document", "Extract data from this spreadsheet",
                "What's in this PDF?")
            file: File to analyze. Can be:
                - File path (str or Path)
                - Raw bytes
                - File-like object (BytesIO, opened file)
            thread_id: Thread ID to continue conversation (empty string creates
                new thread)
            agent: AI agent to use. "UploadPassthroughAgent" (default) for
                direct analysis
            traces: Whether to include reasoning traces in response (default: False)
            share_mode: Visibility - "Private" (default), "Organization", or "Public"
            name: Optional thread name (auto-generated from prompt if not provided)
            filename: Optional filename to use (extracted from path/file
                object if not provided)

        Returns:
            Response object containing AI analysis of the file

        Examples:
            PDF document:
            >>> response = client.upload_binary("Summarize this report", "report.pdf")

            Excel spreadsheet:
            >>> response = client.upload_binary("Extract financial data", "budget.xlsx")

            From bytes:
            >>> with open("document.docx", "rb") as f:
            ...     file_bytes = f.read()
            >>> response = client.upload_binary("Key points from this doc", file_bytes)
        """
        # Get headers with auth
        headers = self._client._get_headers()

        # Serialize binary file
        file_data, file_name, content_type = self._serialize_binary(file, filename)

        # Prepare form data
        files = [("files", (file_name, file_data, content_type))]

        data = {
            "query": prompt,
            "agent": agent,
            "ignore_traces": str(not traces).lower(),
            "share_mode": share_mode,
        }

        # Add optional fields
        if thread_id:
            data["dthread_id"] = thread_id
        if name:
            data["name"] = name

        # Make upload request with streaming response
        response_text = ""
        lines_received = 0
        start_time = time.time()

        # Use configured timeouts
        stream_client = httpx.Client(
            timeout=httpx.Timeout(
                self._client._timeout,  # Overall timeout
                read=self._client._streaming_timeout,  # Per-chunk timeout
            )
        )

        with (
            stream_client,
            stream_client.stream(
                "POST",
                f"{self._client.server_url}/api/chat_upload/",
                headers=headers,
                data=data,
                files=files,
            ) as response,
        ):
            response.raise_for_status()

            # Collect streaming lines
            last_activity = start_time
            try:
                for line in response.iter_lines():
                    if line:
                        response_text += line + "\n"
                        lines_received += 1
                        last_activity = time.time()

                    # Check for timeout
                    time_since_activity = time.time() - last_activity
                    if time_since_activity > self._client._streaming_timeout:
                        logger.warning(
                            f"Streaming timeout after {time_since_activity:.1f}s "
                            f"of inactivity. Received {lines_received} lines."
                        )
                        break

            except httpx.ReadTimeout:
                elapsed = time.time() - start_time
                if lines_received > 0:
                    logger.info(
                        f"Stream ended after {elapsed:.1f}s with {lines_received} lines"
                    )
                else:
                    raise

        # Parse response and create Response object
        parsed = self._client._parse_jsonl_response(response_text)

        # Fetch any dataframes that were returned
        if parsed.get("dthread_id"):
            for elem in parsed.get("elements", []):
                if elem.get("type") in ["DfElement", "df"] and elem.get("id"):
                    # Fetch the actual dataframe
                    fetched_df = self._client._fetch_dataframe_arrow(
                        parsed["dthread_id"], elem["id"]
                    )
                    if fetched_df is not None:
                        elem["table"] = fetched_df

        from ._client import Response

        return Response(
            thread_id=parsed.get("dthread_id", ""), elements=parsed.get("elements", [])
        )

    def _serialize_binary(
        self, file: str | bytes | BinaryIO, filename: str | None = None
    ) -> tuple[bytes, str, str]:
        """Serialize binary file for upload.

        Args:
            file: File in various formats
            filename: Optional filename to use

        Returns:
            Tuple of (file_data, filename, content_type)
        """
        # Handle file path
        if isinstance(file, str | Path):
            path = Path(file)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            # Use provided filename or extract from path
            file_name = filename or path.name

            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(str(path))
            if not mime_type:
                mime_type = "application/octet-stream"

            with open(path, "rb") as f:
                file_data = f.read()

            return file_data, file_name, mime_type

        # Handle bytes
        elif isinstance(file, bytes):
            # Use provided filename or default
            file_name = filename or "file.bin"

            # Try to detect MIME type from filename
            mime_type = None
            if file_name:
                mime_type, _ = mimetypes.guess_type(file_name)

            # Try to detect from content if no MIME type or generic MIME type
            if not mime_type or mime_type == "application/octet-stream":
                # Check for common file signatures
                if file.startswith(b"%PDF"):
                    mime_type = "application/pdf"
                    if not filename:
                        file_name = "document.pdf"
                elif file.startswith(b"PK\x03\x04"):
                    # ZIP-based formats (Office docs, etc.)
                    if b"word/" in file[:1000]:
                        mime_type = (
                            "application/vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        )
                        if not filename:
                            file_name = "document.docx"
                    elif b"xl/" in file[:1000]:
                        mime_type = (
                            "application/vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        )
                        if not filename:
                            file_name = "spreadsheet.xlsx"
                    elif b"ppt/" in file[:1000]:
                        mime_type = (
                            "application/vnd.openxmlformats-officedocument."
                            "presentationml.presentation"
                        )
                        if not filename:
                            file_name = "presentation.pptx"
                    else:
                        mime_type = "application/zip"
                        if not filename:
                            file_name = "archive.zip"
                elif file.startswith(b"{") or file.startswith(b"["):
                    mime_type = "application/json"
                    if not filename:
                        file_name = "data.json"
                else:
                    mime_type = "application/octet-stream"

            return file, file_name, mime_type or "application/octet-stream"

        # Handle file-like objects
        elif hasattr(file, "read"):
            file_data = file.read()
            if hasattr(file, "seek"):
                file.seek(0)  # Reset for potential reuse

            # Try to get filename
            if not filename:
                file_name = getattr(file, "name", "file.bin")
                if isinstance(file_name, str):
                    file_name = os.path.basename(file_name)
                else:
                    file_name = "file.bin"
            else:
                file_name = filename

            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(file_name)
            if not mime_type:
                # Try to detect from content
                if file_data.startswith(b"%PDF"):
                    mime_type = "application/pdf"
                elif file_data.startswith(b"PK\x03\x04"):
                    mime_type = "application/zip"
                else:
                    mime_type = "application/octet-stream"

            return file_data, file_name, mime_type

        else:
            raise TypeError(
                f"Unsupported file type: {type(file)}. "
                "Expected file path, bytes, or file-like object"
            )
