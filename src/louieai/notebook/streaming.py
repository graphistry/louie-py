"""Streaming display support for Jupyter notebooks."""

import json
import time
from typing import Any

try:
    from IPython.display import HTML, clear_output, display, update_display

    HAS_IPYTHON = True
except ImportError:
    HAS_IPYTHON = False

import httpx


class StreamingDisplay:
    """Handle streaming display of Louie responses in Jupyter."""

    def __init__(self, display_id: str | None = None, client=None):
        """Initialize streaming display.

        Args:
            display_id: Optional display ID for updates
            client: Optional LouieClient instance for accessing Graphistry settings
        """
        self.display_id = display_id
        self.client = client
        self.elements_by_id: dict[str, dict[str, Any]] = {}
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
            return str(text).replace("\n", "<br>")

        elif elem_type in ["DfElement", "df"]:
            # Try multiple possible field names for the dataframe ID
            df_id = elem.get("df_id") or elem.get("block_id") or elem.get("id")
            shape = elem.get("metadata", {}).get("shape", ["?", "?"])

            # If we have the actual dataframe, display it
            if "table" in elem and hasattr(elem["table"], "_repr_html_"):
                df_html = elem["table"]._repr_html_()
                if df_html:
                    return (
                        f"<div style='margin: 10px 0;'>"
                        f"<div style='background: #f0f0f0; padding: 5px; "
                        f"margin-bottom: 5px;'>"
                        f"📊 DataFrame {df_id} (shape: {shape[0]} x {shape[1]})</div>"
                        f"{df_html}"
                        f"</div>"
                    )

            # Otherwise show placeholder
            return (
                f"<div style='background: #f0f0f0; padding: 5px; margin: 5px 0;'>"
                f"📊 DataFrame: {df_id} (shape: {shape[0]} x {shape[1]})</div>"
            )

        elif elem_type in ["ExceptionElement", "exception", "error"]:
            msg = elem.get("message", "Unknown error")
            return (
                f"<div style='color: red; background: #ffe0e0; padding: 10px; "
                f"margin: 5px 0;'>⚠️ Error: {msg}</div>"
            )

        elif elem_type == "DebugLine":
            text = elem.get("text", "")
            return (
                f"<div style='color: #666; font-family: monospace; "
                f"font-size: 0.9em;'>🐛 {text}</div>"
            )

        elif elem_type == "InfoLine":
            text = elem.get("text", "")
            return (
                f"<div style='color: #0066cc; font-family: monospace; "
                f"font-size: 0.9em;'>i {text}</div>"
            )

        elif elem_type == "WarningLine":
            text = elem.get("text", "")
            return (
                f"<div style='color: #ff8800; font-family: monospace; "
                f"font-size: 0.9em;'>⚠️ {text}</div>"
            )

        elif elem_type == "ErrorLine":
            text = elem.get("text", "")
            return (
                f"<div style='color: #cc0000; font-family: monospace; "
                f"font-size: 0.9em;'>❌ {text}</div>"
            )

        elif elem_type == "CodeElement":
            code = elem.get("code", "") or elem.get("text", "")
            elem.get("language", "")
            return (
                f"<pre style='background: #f5f5f5; padding: 10px; "
                f"border-radius: 5px;'><code>{code}</code></pre>"
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
                iframe_url = f"{server_url}/graph/graph.html?dataset={dataset_id}"
                return (
                    f'<div style="margin: 10px 0;">'
                    f'<iframe src="{iframe_url}" '
                    f'width="100%" height="600" '
                    f'style="border: 1px solid #ddd; border-radius: 5px;">'
                    f"</iframe>"
                    f'<div style="text-align: center; margin-top: 5px;">'
                    f'<a href="{iframe_url}" target="_blank" '
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
            src = elem.get("src", "")
            width = elem.get("width", "auto")
            height = elem.get("height", "auto")

            # Build style string
            style_parts = ["max-width: 100%", "border-radius: 5px"]
            if width != "auto":
                style_parts.append(f"width: {width}px")
            if height != "auto":
                style_parts.append(f"height: {height}px")

            return (
                f'<div style="margin: 10px 0; text-align: center;">'
                f'<img src="{src}" style="{";".join(style_parts)}" />'
                f"</div>"
            )

        elif elem_type == "BinaryElement":
            # Handle binary elements with URLs
            url = elem.get("url", "")
            content_type = elem.get("content_type", "")
            filename = elem.get("filename", "download")
            size = elem.get("size", 0)

            # If URL is relative, prepend base URL from client
            if url and not url.startswith(("http://", "https://")):
                base_url = "https://api.louie.ai"  # default
                if self.client and hasattr(self.client, "base_url"):
                    base_url = self.client.base_url.rstrip("/")
                url = f"{base_url}{url}"

            # Check if it's an image
            if content_type and content_type.startswith("image/"):
                return (
                    f'<div style="margin: 10px 0; text-align: center;">'
                    f'<img src="{url}" style="max-width: 100%; border-radius: 5px;" />'
                    f'<div style="text-align: center; margin-top: 5px;">'
                    f'<a href="{url}" download="{filename}" '
                    f'style="color: #0066cc; text-decoration: none; font-size: 0.9em;">'
                    f"📥 Download {filename}</a>"
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
                    f'<span style="font-weight: bold;">📎 {filename}</span>'
                    + (
                        f' <span style="color: #666; font-size: 0.9em;">'
                        f"({size_str})</span>"
                        if size_str
                        else ""
                    )
                    + f"</div>"
                    f'<a href="{url}" download="{filename}" '
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
            if text:
                return f"<div style='color: gray;'>[{elem_type}] {text}</div>"
            else:
                return f"<div style='color: gray;'>[{elem_type}]</div>"

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
                f"Thread: <code>{self.thread_id}</code> | "
                f"Time: {elapsed:.1f}s"
                f"</div>"
            )

        # Render elements
        if self.elements_by_id:
            parts.append("<div style='margin-top: 10px;'>")
            for elem_id, elem in self.elements_by_id.items():
                formatted = self._format_element(elem)
                parts.append(f"<div id='{elem_id}'>{formatted}</div>")
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
        # Handle thread ID
        if "dthread_id" in data:
            self.thread_id = data["dthread_id"]

        # Handle payload updates
        elif "payload" in data:
            elem = data["payload"]
            elem_id = elem.get("id")

            if elem_id:
                # Update element
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
    """Stream a response with real-time display in Jupyter.

    Args:
        client: LouieClient instance
        thread_id: Thread ID (empty string for new thread)
        prompt: Query prompt
        **kwargs: Additional parameters (agent, traces, share_mode, etc.)

    Returns:
        Dict with thread_id and elements
    """
    # Extract parameters
    agent = kwargs.get("agent", "LouieAgent")
    traces = kwargs.get("traces", False)
    share_mode = kwargs.get("share_mode", "Private")

    # Get headers
    headers = client._get_headers()

    # Build parameters
    params = {
        "query": prompt,
        "agent": agent,
        "ignore_traces": str(not traces).lower(),
        "share_mode": share_mode,
    }

    if thread_id:
        params["dthread_id"] = thread_id

    # Create display handler with client for Graphistry URL
    display_handler = StreamingDisplay(client=client)

    # Result to return
    result: dict[str, Any] = {"dthread_id": None, "elements": []}
    elements_by_id = {}

    # Make streaming request
    try:
        with (
            httpx.Client(timeout=httpx.Timeout(300.0, read=120.0)) as stream_client,
            stream_client.stream(
                "POST", f"{client.server_url}/api/chat/", headers=headers, params=params
            ) as response,
        ):
            response.raise_for_status()

            # Process streaming lines
            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    data = json.loads(line)

                    # Update display
                    display_handler.update(data)

                    # Track data for result
                    if "dthread_id" in data:
                        result["dthread_id"] = data["dthread_id"]

                    elif "payload" in data:
                        elem = data["payload"]
                        elem_id = elem.get("id")
                        if elem_id:
                            elements_by_id[elem_id] = elem

                except json.JSONDecodeError:
                    continue

    except httpx.ReadTimeout:
        # This is expected - server keeps connection open
        pass
    except Exception as e:
        # Show error in display
        error_elem = {"id": "error", "type": "ExceptionElement", "message": str(e)}
        display_handler.elements_by_id["error"] = error_elem
        display_handler.finalize()
        raise

    # Final update
    display_handler.finalize()

    # Convert to list for result
    result["elements"] = list(elements_by_id.values())

    # Fetch dataframes if needed
    actual_thread_id = result["dthread_id"]
    if actual_thread_id and result["elements"]:
        for elem in result["elements"]:
            if elem.get("type") in ["DfElement", "df"]:
                # Try multiple possible field names for the dataframe ID
                df_id = elem.get("df_id") or elem.get("block_id") or elem.get("id")

                if df_id:
                    # Fetch the actual dataframe via Arrow
                    df = client._fetch_dataframe_arrow(actual_thread_id, df_id)
                    if df is not None:
                        elem["table"] = df

    return result
