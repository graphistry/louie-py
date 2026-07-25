"""Streaming display support for Jupyter notebooks."""

import html
import time
from typing import Any

try:
    from IPython.display import HTML, clear_output, display, update_display

    HAS_IPYTHON = True
except ImportError:
    HAS_IPYTHON = False

import httpx

from .._client import LouieClient, Response
from ._html import (
    css_pixel_dimension,
    graph_url,
    resolve_http_url,
    safe_image_src,
)


class StreamingDisplay:
    """Handle streaming display of Louie responses in Jupyter."""

    def __init__(
        self,
        display_id: str | None = None,
        client=None,
        include_reasoning: bool | None = None,
    ):
        """Initialize streaming display.

        Args:
            display_id: Optional display ID for updates
            client: Optional LouieClient instance for accessing Graphistry settings
            include_reasoning: Whether structural reasoning was requested.
        """
        self.display_id = display_id
        self.client = client
        self.include_reasoning = include_reasoning
        self.elements_by_id: dict[str, dict[str, Any]] = {}
        self.position_keys: dict[int, str] = {}
        self.stream_messages: list[dict[str, Any]] = []
        self.thread_id: str | None = None
        self.start_time = time.time()
        self.last_update_time = 0.0

    def _format_element(self, elem: dict[str, Any]) -> str:
        """Format an element for display."""
        elem_type = elem.get("type", "")

        if elem_type in ["TextElement", "text"]:
            # Handle both 'text' and 'value' fields
            text = elem.get("text", "") or elem.get("value", "")
            # Convert newlines to HTML breaks
            return html.escape(str(text)).replace("\n", "<br>")

        elif elem_type in ["DfElement", "df"]:
            # Try multiple possible field names for the dataframe ID
            df_id = elem.get("df_id") or elem.get("block_id") or elem.get("id")
            shape = elem.get("metadata", {}).get("shape", ["?", "?"])
            if not isinstance(shape, list | tuple) or len(shape) < 2:
                shape = ["?", "?"]
            safe_df_id = html.escape(str(df_id))
            safe_rows = html.escape(str(shape[0]))
            safe_columns = html.escape(str(shape[1]))
            safe_shape = f"{safe_rows} x {safe_columns}"

            # If we have the actual dataframe, display it
            if "table" in elem and hasattr(elem["table"], "_repr_html_"):
                df_html = elem["table"]._repr_html_()
                if df_html:
                    return (
                        f"<div style='margin: 10px 0;'>"
                        f"<div style='background: #f0f0f0; padding: 5px; "
                        f"margin-bottom: 5px;'>"
                        f"📊 DataFrame {safe_df_id} (shape: {safe_shape})</div>"
                        f"{df_html}"
                        f"</div>"
                    )

            # Otherwise show placeholder
            return (
                f"<div style='background: #f0f0f0; padding: 5px; margin: 5px 0;'>"
                f"📊 DataFrame: {safe_df_id} (shape: {safe_shape})</div>"
            )

        elif elem_type in ["ExceptionElement", "exception", "error"]:
            msg = elem.get("message", "Unknown error")
            return (
                f"<div style='color: red; background: #ffe0e0; padding: 10px; "
                f"margin: 5px 0;'>⚠️ Error: {html.escape(str(msg))}</div>"
            )

        elif elem_type == "DebugLine":
            text = elem.get("text", "")
            return (
                f"<div style='color: #666; font-family: monospace; "
                f"font-size: 0.9em;'>🐛 {html.escape(str(text))}</div>"
            )

        elif elem_type == "InfoLine":
            text = elem.get("text", "")
            return (
                f"<div style='color: #0066cc; font-family: monospace; "
                f"font-size: 0.9em;'>i {html.escape(str(text))}</div>"
            )

        elif elem_type == "WarningLine":
            text = elem.get("text", "")
            return (
                f"<div style='color: #ff8800; font-family: monospace; "
                f"font-size: 0.9em;'>⚠️ {html.escape(str(text))}</div>"
            )

        elif elem_type == "ErrorLine":
            text = elem.get("text", "")
            return (
                f"<div style='color: #cc0000; font-family: monospace; "
                f"font-size: 0.9em;'>❌ {html.escape(str(text))}</div>"
            )

        elif elem_type == "CodeElement":
            code = elem.get("code", "") or elem.get("text", "")
            elem.get("language", "")
            escaped_code = html.escape(str(code), quote=False)
            return (
                f"<pre style='background: #f5f5f5; padding: 10px; "
                f"border-radius: 5px;'><code>{escaped_code}</code></pre>"
            )

        elif elem_type in ["GraphElement", "graph"]:
            # Extract dataset_id - try multiple possible locations
            dataset_id = None

            # First try: element['value']['dataset_id']
            value = elem.get("value", {})
            if isinstance(value, dict):
                dataset_id = value.get("dataset_id")

            # Second try: element['dataset_id'] directly
            if not dataset_id:
                dataset_id = elem.get("dataset_id")

            # Third try: element['id'] as fallback
            if not dataset_id:
                dataset_id = elem.get("id")

            # Get Graphistry server URL from client if available
            server_url = "https://hub.graphistry.com"  # default
            if self.client and hasattr(self.client, "_auth_manager"):
                try:
                    g = self.client._auth_manager._graphistry_client
                    if hasattr(g, "client_protocol_hostname") and hasattr(
                        g, "protocol"
                    ):
                        hostname = g.client_protocol_hostname()
                        protocol = g.protocol()

                        if hostname:
                            # Fix malformed protocols first
                            hostname = hostname.replace("https//", "https://")
                            hostname = hostname.replace("http//", "http://")

                            # Check if hostname already contains protocol
                            if hostname.startswith(("http://", "https://")):
                                # It's a full URL already
                                server_url = hostname
                            else:
                                # It's just a hostname, need to add protocol
                                # Use protocol from g.protocol() if available
                                if not protocol:
                                    protocol = "https://"
                                # Ensure protocol ends with ://
                                if protocol and not protocol.endswith("://"):
                                    if protocol.endswith(":/"):
                                        protocol = protocol + "/"
                                    elif protocol.endswith(":"):
                                        protocol = protocol + "//"
                                    else:
                                        protocol = protocol + "://"
                                server_url = f"{protocol}{hostname}"
                except Exception:
                    pass  # Use default

            if dataset_id:
                # Create iframe for Graphistry visualization
                iframe_url = graph_url(server_url, dataset_id)
                if iframe_url is None:
                    return (
                        "<div style='color: #888; padding: 10px;'>"
                        "Graph visualization not available</div>"
                    )
                safe_iframe_url = html.escape(iframe_url, quote=True)
                return (
                    f'<div style="margin: 10px 0;">'
                    f'<iframe src="{safe_iframe_url}" '
                    f'width="100%" height="600" '
                    f'style="border: 1px solid #ddd; border-radius: 5px;">'
                    f"</iframe>"
                    f'<div style="text-align: center; margin-top: 5px;">'
                    f'<a href="{safe_iframe_url}" target="_blank" '
                    f'rel="noopener noreferrer" '
                    f'style="color: #0066cc; text-decoration: none;">'
                    f"🔗 Open graph in new tab</a>"
                    f"</div>"
                    f"</div>"
                )
            else:
                # Show placeholder for missing dataset_id
                return (
                    f"<div style='color: #888; padding: 10px; "
                    f"background: #f5f5f5; margin: 5px 0;'>"
                    f"[{elem_type}] Graph visualization not available</div>"
                )

        elif elem_type == "Base64ImageElement":
            # Handle inline base64 images
            src = safe_image_src(elem.get("src", ""))
            if src is None:
                return "<div style='color: #888;'>Image unavailable</div>"
            safe_src = html.escape(src, quote=True)
            width = css_pixel_dimension(elem.get("width"))
            height = css_pixel_dimension(elem.get("height"))

            # Build style string from validated numeric dimensions only.
            style_parts = ["max-width: 100%", "border-radius: 5px"]
            if width is not None:
                style_parts.append(f"width: {width}px")
            if height is not None:
                style_parts.append(f"height: {height}px")

            return (
                f'<div style="margin: 10px 0; text-align: center;">'
                f'<img src="{safe_src}" style="{";".join(style_parts)}" />'
                f"</div>"
            )

        elif elem_type == "BinaryElement":
            # Handle binary elements with URLs
            url = elem.get("url", "")
            content_type = elem.get("content_type", "")
            filename = elem.get("filename", "download")
            size = elem.get("size", 0)

            base_url = "https://api.louie.ai"
            if self.client:
                base_url = getattr(
                    self.client,
                    "server_url",
                    getattr(self.client, "base_url", base_url),
                )
            resolved_url = resolve_http_url(url, base_url)
            safe_filename = html.escape(str(filename), quote=True)
            if resolved_url is None:
                return (
                    f"<div style='color: #888;'>File unavailable: {safe_filename}</div>"
                )
            safe_url = html.escape(resolved_url, quote=True)

            # Check if it's an image
            if content_type and content_type.startswith("image/"):
                return (
                    f'<div style="margin: 10px 0; text-align: center;">'
                    f'<img src="{safe_url}" '
                    f'style="max-width: 100%; border-radius: 5px;" />'
                    f'<div style="text-align: center; margin-top: 5px;">'
                    f'<a href="{safe_url}" download="{safe_filename}" '
                    f'style="color: #0066cc; text-decoration: none; font-size: 0.9em;">'
                    f"📥 Download {safe_filename}</a>"
                    f"</div>"
                    f"</div>"
                )
            else:
                # Non-image binary file - show download link
                size_str = ""
                if size > 0:
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.1f} MB"

                return (
                    f'<div style="margin: 10px 0; padding: 10px; background: #f5f5f5; '
                    f'border-radius: 5px; border: 1px solid #ddd;">'
                    f'<div style="display: flex; align-items: center; '
                    f'justify-content: space-between;">'
                    f"<div>"
                    f'<span style="font-weight: bold;">📎 {safe_filename}</span>'
                    + (
                        f' <span style="color: #666; font-size: 0.9em;">'
                        f"({size_str})</span>"
                        if size_str
                        else ""
                    )
                    + f"</div>"
                    f'<a href="{safe_url}" download="{safe_filename}" '
                    f'style="background: #0066cc; color: white; padding: 5px 15px; '
                    f'border-radius: 3px; text-decoration: none;">Download</a>'
                    f"</div>"
                    f"</div>"
                )

        else:
            # For unknown types, try to extract text or show raw content
            text = (
                elem.get("text", "")
                or elem.get("content", "")
                or str(elem.get("value", ""))
            )
            safe_type = html.escape(str(elem_type))
            if text:
                safe_text = html.escape(str(text))
                return f"<div style='color: gray;'>[{safe_type}] {safe_text}</div>"
            return f"<div style='color: gray;'>[{safe_type}]</div>"

    def _render_element(self, elem: dict[str, Any]) -> str:
        """Backwards-compatible alias for element rendering."""
        return self._format_element(elem)

    def _render_html(self) -> str:
        """Render current state as HTML."""
        parts = [
            "<div style='border: 1px solid #ddd; padding: 15px; border-radius: 5px;'>",
            "<h4 style='margin-top: 0;'>🤖 LouieAI Response</h4>",
        ]

        # Show thread ID if available
        if self.thread_id:
            elapsed = time.time() - self.start_time
            parts.append(
                f"<div style='font-size: 0.8em; color: #666; margin-bottom: 10px;'>"
                f"Thread: <code>{html.escape(str(self.thread_id))}</code> | "
                f"Time: {elapsed:.1f}s"
                f"</div>"
            )

        snapshot = Response(
            thread_id=self.thread_id or "",
            elements=list(self.elements_by_id.values()),
            stream_messages=self.stream_messages,
            include_reasoning=self.include_reasoning,
        )
        if snapshot.status != "unknown":
            parts.append(
                "<div style='font-size: 0.9em; margin-bottom: 8px;'>"
                f"<b>Status:</b> {html.escape(snapshot.status)}</div>"
            )
        if snapshot.phases:
            parts.append("<details><summary><b>Execution phases</b></summary><ul>")
            for phase in snapshot.phases:
                action = phase.get("action")
                expression = (
                    action.get("expression") if isinstance(action, dict) else None
                )
                label = (
                    expression or phase.get("run_type") or phase.get("id") or "phase"
                )
                state = phase.get("state", "unknown")
                parts.append(
                    f"<li>{html.escape(str(label))}: {html.escape(str(state))}</li>"
                )
            parts.append("</ul></details>")

        # Render elements, collapsing identifiable reasoning by default.
        if self.elements_by_id:
            reasoning_ids = {
                str(element.get("id"))
                for element in snapshot.reasoning_elements
                if element.get("id") is not None
            }
            parts.append("<div style='margin-top: 10px;'>")
            for elem_id, elem in self.elements_by_id.items():
                formatted = self._format_element(elem)
                safe_id = html.escape(str(elem_id), quote=True)
                if str(elem.get("id")) in reasoning_ids:
                    parts.append(
                        "<details style='margin: 5px 0;'>"
                        "<summary><b>Reasoning</b></summary>"
                        f"<div id='{safe_id}'>{formatted}</div></details>"
                    )
                else:
                    parts.append(f"<div id='{safe_id}'>{formatted}</div>")
            parts.append("</div>")
        else:
            parts.append("<div style='color: #999;'>Waiting for response...</div>")

        parts.append("</div>")
        return "".join(parts)

    def update(self, data: dict[str, Any]) -> None:
        """Update display with new data from stream.

        Args:
            data: Parsed JSON data from stream
        """
        self.stream_messages.append(data)

        # Handle thread ID
        if "dthread_id" in data:
            self.thread_id = data["dthread_id"]

        # Route by type discriminator (new servers),
        # fall back to payload check (old servers)
        msg_type = data.get("type")

        if msg_type == "StreamingApiMessageOutputUpdate":
            elem = data.get("payload")
            if isinstance(elem, dict):
                position = data.get("position")
                elem_key = str(
                    elem.get("id")
                    or (f"position:{position}" if isinstance(position, int) else "")
                )
                if elem_key:
                    if isinstance(position, int):
                        previous_key = self.position_keys.get(position)
                        if previous_key and previous_key != elem_key:
                            self.elements_by_id.pop(previous_key, None)
                        self.position_keys[position] = elem_key
                    existing = self.elements_by_id.get(elem_key, {})
                    self.elements_by_id[elem_key] = {**existing, **elem}

        elif msg_type in (
            "StreamingApiMessageRunUpdate",
            "StreamingApiMessageTrace",
            "StreamingApiMessageStart",
            "StreamingApiMessageTerminal",
        ):
            pass  # Non-element messages, skip

        elif msg_type is None and "payload" in data:
            # Legacy fallback: old servers without type field
            elem = data["payload"]
            if isinstance(elem, dict):
                elem_id = elem.get("id")
                if elem_id:
                    self.elements_by_id[elem_id] = elem

        # Update display if in Jupyter
        if HAS_IPYTHON:
            # Throttle updates to avoid flicker (max 10 updates per second)
            current_time = time.time()
            if current_time - self.last_update_time > 0.1:
                html = self._render_html()

                if self.display_id:
                    update_display(HTML(html), display_id=self.display_id)
                else:
                    clear_output(wait=True)
                    display(HTML(html))

                self.last_update_time = current_time

    def finalize(self) -> None:
        """Final display update when streaming is complete."""
        if HAS_IPYTHON:
            html = self._render_html()
            if self.display_id:
                update_display(HTML(html), display_id=self.display_id)
            else:
                clear_output(wait=True)
                display(HTML(html))


def stream_response(client, thread_id: str, prompt: str, **kwargs) -> dict[str, Any]:
    """Stream a response with display and the shared lossless accumulator."""
    agent = kwargs.get("agent", "LouieAgent")
    traces = kwargs.get("traces", False)
    include_reasoning = kwargs.get("include_reasoning", False)
    share_mode = kwargs.get("share_mode", "Private")
    user_agent = kwargs.get("user_agent", "API")
    name = kwargs.get("name")
    folder = kwargs.get("folder")
    session_trace_id = kwargs.get("session_trace_id")

    headers = client._get_headers(session_trace_id=session_trace_id)
    params = {
        "query": prompt,
        "agent": agent,
        "ignore_traces": str(not traces).lower(),
        "include_reasoning": str(include_reasoning).lower(),
        "user_agent": user_agent,
        "share_mode": share_mode,
    }
    if thread_id:
        params["dthread_id"] = thread_id
    else:
        if name:
            params["name"] = name
        if folder:
            params["folder"] = folder

    display_handler = StreamingDisplay(
        client=client, include_reasoning=include_reasoning
    )
    overall_timeout = client._timeout
    read_timeout = client._streaming_timeout
    lines_received = 0
    response_chunks: list[str] = []

    try:
        with (
            httpx.Client(
                timeout=httpx.Timeout(overall_timeout, read=read_timeout)
            ) as stream_client,
            stream_client.stream(
                "POST",
                f"{client.server_url}/api/chat/",
                headers=headers,
                params=params,
            ) as response,
        ):
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                lines_received += 1
                response_chunks.append(f"{line}\n")
                for data in LouieClient._decode_json_objects(line):
                    display_handler.update(data)

    except httpx.ReadTimeout:
        import warnings

        timeout_msg = (
            f"Streaming timed out after {lines_received} lines "
            f"(read_timeout={read_timeout:.0f}s). "
            f"Increase streaming_timeout when creating LouieClient."
        )
        warnings.warn(timeout_msg, RuntimeWarning, stacklevel=2)
    except Exception as exc:
        error_elem = {
            "id": "error",
            "type": "ExceptionElement",
            "message": str(exc),
        }
        display_handler.elements_by_id["error"] = error_elem
        display_handler.finalize()
        raise

    objects = LouieClient._decode_json_objects("".join(response_chunks))
    result = LouieClient._parse_stream_objects(objects)
    result["dthread_id"] = result.get("dthread_id") or thread_id

    actual_thread_id = result["dthread_id"]
    if actual_thread_id and result["elements"]:
        for elem in result["elements"]:
            if elem.get("type") in ["DfElement", "df"]:
                shape = (elem.get("metadata") or {}).get("shape", [])
                if shape and shape[0] == 0:
                    import pandas as pd

                    elem["table"] = pd.DataFrame()
                    continue
                df_id = elem.get("df_id") or elem.get("block_id") or elem.get("id")
                if df_id:
                    df = client._fetch_dataframe_arrow(actual_thread_id, df_id)
                    if df is not None:
                        elem["table"] = df

    display_handler.thread_id = actual_thread_id or None
    display_handler.stream_messages = result["stream_messages"]
    display_handler.elements_by_id = {
        str(elem.get("id") or f"position:{index}"): elem
        for index, elem in enumerate(result["elements"])
    }
    display_handler.finalize()
    return result
