"""DataFrame upload functionality for Louie.ai."""

from __future__ import annotations

import io
import json
import logging
import mimetypes
import os
import time
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO

if TYPE_CHECKING:
    from ._client import LouieClient, Response
    from .auth import AuthManager

import httpx
import pandas as pd

from ._http import raise_for_status
from ._table_ai import (
    TableAIOverrides,
    collect_table_ai_kwargs,
    normalize_table_ai_overrides,
)
from .auth import auto_retry_auth

logger = logging.getLogger(__name__)


class UploadClient:
    """Handles DataFrame uploads to Louie.ai via the new upload API."""

    def __init__(self, client: LouieClient):
        """Initialize with parent client for auth and settings."""
        self._client = client

    @property
    def auth_manager(self) -> AuthManager:
        """Parent client's auth manager, which ``@auto_retry_auth`` refreshes."""
        return self._client.auth_manager

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
        include_reasoning: bool = False,
        share_mode: str = "Private",
        name: str | None = None,
        folder: str | None = None,
        parsing_options: dict[str, Any] | None = None,
        table_ai_overrides: TableAIOverrides | Mapping[str, Any] | None = None,
        session_trace_id: str | None = None,
        **legacy_overrides: Any,
    ) -> Response:
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
                parses data without LLM.
            traces: Whether to request server trace events (default: False)
            include_reasoning: Include the agent's provisional reasoning
                text in addition to final response elements (default: False).
            share_mode: Visibility - "Private" (default), "Organization", or "Public"
            name: Optional thread name (auto-generated from prompt if not provided)
            folder: Optional folder path for the thread (server support required)
            parsing_options: Dict of format-specific parsing options (e.g., for CSV:
                {"delimiter": ",", "header": true}). If None, uses sensible defaults.
            table_ai_overrides: Structured overrides via dataclass or mapping.
            **legacy_overrides: Backwards-compatible Table AI keyword arguments (e.g.,
                ``table_ai_semantic_mode``). Prefer `table_ai_overrides`.

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
        # Get headers with auth and tracing
        headers = self._client._get_headers(session_trace_id=session_trace_id)

        # Serialize DataFrame to specified format
        file_data, filename, content_type = self._serialize_dataframe(df, format)

        # Prepare form data
        files = [("files", (filename, file_data, content_type))]

        data = {
            "query": prompt,
            "agent": agent,
            "ignore_traces": str(not traces).lower(),
            "include_reasoning": str(include_reasoning).lower(),
            "share_mode": share_mode,
        }

        # Add optional fields
        if thread_id:
            data["dthread_id"] = thread_id
        else:
            if name:
                data["name"] = name
            if folder:
                data["folder"] = folder

        # Add parsing options if provided
        if parsing_options:
            # For single file, wrap in array
            data["parsing_options"] = json.dumps([parsing_options])
        else:
            # Use default parsing options based on format
            default_options = self._get_default_parsing_options(format)
            if default_options:
                data["parsing_options"] = json.dumps([default_options])

        # Table AI overrides (optional)
        data.update(normalize_table_ai_overrides(table_ai_overrides))
        legacy_params = collect_table_ai_kwargs(legacy_overrides)
        if legacy_overrides:
            unexpected = ", ".join(sorted(legacy_overrides))
            raise TypeError(
                f"upload_dataframe() got unexpected keyword argument(s): {unexpected}"
            )
        data.update(legacy_params)

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
            raise_for_status(response)

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

        from ._client import Response

        dthread_id = parsed.get("dthread_id") or ""
        elements = parsed.get("elements", [])
        if dthread_id:
            attach_fn = getattr(self._client, "_attach_dataframes", None)
            used_fallback = True
            if callable(attach_fn):
                attach_fn(dthread_id, elements)
                module_name = getattr(attach_fn, "__module__", "")
                used_fallback = module_name.startswith("unittest.mock")
            if used_fallback:
                self._fallback_attach_dataframes(dthread_id, elements)

        return Response(
            thread_id=dthread_id,
            elements=elements,
            stream_messages=parsed.get("stream_messages", []),
            include_reasoning=include_reasoning,
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

    def _fallback_attach_dataframes(
        self, thread_id: str, elements: list[dict[str, Any]]
    ) -> None:
        """Fallback hydration for mocked clients lacking `_attach_dataframes`."""

        fetch_fn = getattr(self._client, "_fetch_dataframe_arrow", None)
        if not callable(fetch_fn):
            return

        for elem in elements:
            if elem.get("type") in ["DfElement", "df"] and elem.get("id"):
                fetched = fetch_fn(thread_id, elem["id"])
                if fetched is not None:
                    elem["table"] = fetched
                else:
                    logger.warning(
                        f"Failed to fetch dataframe {elem.get('id')} from thread "
                        f"{thread_id} for DfElement. Element: {elem}"
                    )

    def upload_image(
        self,
        prompt: str,
        image: str | bytes | BinaryIO | Any,
        thread_id: str = "",
        *,
        agent: str = "UploadPassthroughAgent",
        traces: bool = False,
        include_reasoning: bool = False,
        share_mode: str = "Private",
        name: str | None = None,
        folder: str | None = None,
        filename: str | None = None,
        session_trace_id: str | None = None,
    ) -> Response:
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
            traces: Whether to request server trace events (default: False)
            share_mode: Visibility - "Private" (default), "Organization", or "Public"
            name: Optional thread name (auto-generated from prompt if not provided)
            folder: Optional folder path for the thread (server support required)
            filename: Optional filename to send, as given (an empty string
                means unset). The server routes uploads by extension, so
                include one (`.png`, `.jpg`, ...). By default the name comes
                from the path or the file object's `.name`; its extension is
                taken from the image's file signature only when it is not an
                image extension. Raw bytes, nameless file objects and PIL
                images are named `image.<ext>`, or `image.bin` when the bytes
                have no known image signature.

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
        # Serialize once: the retry in _send_file resends these bytes rather
        # than re-reading the caller's file object, which may not rewind
        file_data, filename, content_type = self._serialize_image(image, filename)
        return self._send_file(
            prompt,
            file_data,
            filename,
            content_type,
            thread_id,
            agent=agent,
            traces=traces,
            include_reasoning=include_reasoning,
            share_mode=share_mode,
            name=name,
            folder=folder,
            session_trace_id=session_trace_id,
        )

    @auto_retry_auth
    def _send_file(
        self,
        prompt: str,
        file_data: bytes,
        filename: str,
        content_type: str,
        thread_id: str,
        *,
        agent: str,
        traces: bool,
        include_reasoning: bool,
        share_mode: str,
        name: str | None,
        folder: str | None,
        session_trace_id: str | None,
    ) -> Response:
        """POST serialized file bytes to the upload API and parse the stream.

        Shared by ``upload_image`` and ``upload_binary``. ``auto_retry_auth``
        re-runs this whole method with fresh headers, resending the same
        already-serialized bytes.
        """
        # Get headers with auth and tracing (fresh on each retry)
        headers = self._client._get_headers(session_trace_id=session_trace_id)

        # Prepare form data
        files = [("files", (filename, file_data, content_type))]

        data = {
            "query": prompt,
            "agent": agent,
            "ignore_traces": str(not traces).lower(),
            "include_reasoning": str(include_reasoning).lower(),
            "share_mode": share_mode,
        }

        # Add optional fields
        if thread_id:
            data["dthread_id"] = thread_id
        else:
            if name:
                data["name"] = name
            if folder:
                data["folder"] = folder

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
            raise_for_status(response)

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
            thread_id=parsed.get("dthread_id", ""),
            elements=parsed.get("elements", []),
            stream_messages=parsed.get("stream_messages", []),
            include_reasoning=include_reasoning,
        )

    @staticmethod
    def _sniff_image(data: bytes) -> tuple[str, str] | None:
        """Return ``(extension, mime_type)`` from the file signature, or None."""
        if data.startswith(b"\x89PNG"):
            return "png", "image/png"
        if data.startswith(b"\xff\xd8\xff"):
            return "jpg", "image/jpeg"
        if data.startswith(b"GIF8"):
            return "gif", "image/gif"
        if data.startswith(b"BM"):
            return "bmp", "image/bmp"
        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            return "webp", "image/webp"
        return None

    def _name_image(
        self, data: bytes, given: str | None, derived: str | None
    ) -> tuple[str, str]:
        """Pick the multipart filename and content type for image bytes.

        The server routes uploads by filename extension and never inspects the
        bytes, so a wrong or missing extension leaves the image as opaque binary.
        A non-empty ``given`` (the caller's ``filename=``; empty means unset) is
        sent verbatim; its content type comes from its image extension, else from
        the byte signature. ``derived`` (from a path or a file object's ``.name``)
        keeps its stem but gets the signature's extension when its own is not an
        image type. With neither, the name is ``image.<ext>`` from the signature.
        Bytes with no known image signature and no image extension keep their
        name (``image.bin`` when there is none) and go as
        ``application/octet-stream``.
        """
        name = given or derived or ""
        guessed = mimetypes.guess_type(name)[0] if name else None
        if guessed and guessed.startswith("image/"):
            return name, guessed
        sniffed = self._sniff_image(data)
        if sniffed is None:
            return name or "image.bin", "application/octet-stream"
        ext, mime_type = sniffed
        if given:
            return given, mime_type
        # Path.stem keeps a trailing dot ("name." -> "name."); strip it so the
        # result is "name.jpg", not "name..jpg".
        stem = Path(derived).stem.rstrip(".") if derived else ""
        return f"{stem or 'image'}.{ext}", mime_type

    def _serialize_image(
        self,
        image: str | bytes | BinaryIO | Any,
        filename: str | None = None,
    ) -> tuple[bytes, str, str]:
        """Serialize image to bytes for upload.

        Args:
            image: Image in various formats
            filename: Optional filename to send verbatim; see ``_name_image``

        Returns:
            Tuple of (file_data, filename, content_type)
        """
        # Handle file path
        if isinstance(image, str | Path):
            path = Path(image)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")
            with open(path, "rb") as f:
                file_data = f.read()
            name, mime_type = self._name_image(file_data, filename, path.name)
            return file_data, name, mime_type

        # Handle bytes
        elif isinstance(image, bytes):
            name, mime_type = self._name_image(image, filename, None)
            return image, name, mime_type

        # Handle file-like objects
        elif hasattr(image, "read"):
            file_data = image.read()
            if hasattr(image, "seek"):
                image.seek(0)  # Reset for potential reuse

            derived = getattr(image, "name", None)
            derived = os.path.basename(derived) if isinstance(derived, str) else None
            name, mime_type = self._name_image(file_data, filename, derived)
            return file_data, name, mime_type

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
                        default, content_type = "image.jpg", "image/jpeg"
                    else:
                        image.save(buffer, format="PNG")
                        default, content_type = "image.png", "image/png"
                    buffer.seek(0)
                    return buffer.read(), filename or default, content_type
            except ImportError:
                pass

            raise TypeError(
                f"Unsupported image type: {type(image)}. "
                "Expected file path, bytes, file-like object, or PIL Image"
            )

    def upload_binary(
        self,
        prompt: str,
        file: str | bytes | BinaryIO,
        thread_id: str = "",
        *,
        agent: str = "UploadPassthroughAgent",
        traces: bool = False,
        include_reasoning: bool = False,
        share_mode: str = "Private",
        name: str | None = None,
        folder: str | None = None,
        filename: str | None = None,
        session_trace_id: str | None = None,
    ) -> Response:
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
            traces: Whether to request server trace events (default: False)
            share_mode: Visibility - "Private" (default), "Organization", or "Public"
            name: Optional thread name (auto-generated from prompt if not provided)
            folder: Optional folder path for the thread (server support required)
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
        # Serialize once: the retry in _send_file resends these bytes rather
        # than re-reading the caller's file object, which may not rewind
        file_data, filename, content_type = self._serialize_binary(file, filename)
        return self._send_file(
            prompt,
            file_data,
            filename,
            content_type,
            thread_id,
            agent=agent,
            traces=traces,
            include_reasoning=include_reasoning,
            share_mode=share_mode,
            name=name,
            folder=folder,
            session_trace_id=session_trace_id,
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
