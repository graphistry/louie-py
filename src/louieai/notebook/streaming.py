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

    def __init__(self, display_id: str | None = None):
        """Initialize streaming display.

        Args:
            display_id: Optional display ID for updates
        """
        self.display_id = display_id
        self.elements_by_id: dict[str, dict[str, Any]] = {}
        self.thread_id: str | None = None
        self.start_time = time.time()
        self.last_update_time = 0.0

    def _format_element(self, elem: dict[str, Any]) -> str:
        """Format an element for display."""
        elem_type = elem.get("type", "")

        if elem_type == "TextElement":
            text = elem.get("text", "")
            # Convert newlines to HTML breaks
            return text.replace("\n", "<br>")

        elif elem_type == "DfElement":
            df_id = elem.get("df_id") or elem.get("block_id")
            shape = elem.get("metadata", {}).get("shape", ["?", "?"])
            return f"<div style='background: #f0f0f0; padding: 5px; margin: 5px 0;'>📊 DataFrame: {df_id} (shape: {shape[0]} × {shape[1]})</div>"

        elif elem_type == "ExceptionElement":
            msg = elem.get("message", "Unknown error")
            return f"<div style='color: red; background: #ffe0e0; padding: 10px; margin: 5px 0;'>⚠️ Error: {msg}</div>"

        elif elem_type == "DebugLine":
            text = elem.get("text", "")
            return f"<div style='color: #666; font-family: monospace; font-size: 0.9em;'>🐛 {text}</div>"

        elif elem_type == "InfoLine":
            text = elem.get("text", "")
            return f"<div style='color: #0066cc; font-family: monospace; font-size: 0.9em;'>ℹ️ {text}</div>"

        elif elem_type == "WarningLine":
            text = elem.get("text", "")
            return f"<div style='color: #ff8800; font-family: monospace; font-size: 0.9em;'>⚠️ {text}</div>"

        elif elem_type == "ErrorLine":
            text = elem.get("text", "")
            return f"<div style='color: #cc0000; font-family: monospace; font-size: 0.9em;'>❌ {text}</div>"

        elif elem_type == "CodeElement":
            code = elem.get("code", "") or elem.get("text", "")
            elem.get("language", "")
            return f"<pre style='background: #f5f5f5; padding: 10px; border-radius: 5px;'><code>{code}</code></pre>"

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

    # Create display handler
    display_handler = StreamingDisplay()

    # Result to return
    result = {"dthread_id": None, "elements": []}
    elements_by_id = {}

    # Make streaming request
    try:
        with httpx.Client(timeout=httpx.Timeout(300.0, read=120.0)) as stream_client:
            with stream_client.stream(
                "POST", f"{client.server_url}/api/chat/", headers=headers, params=params
            ) as response:
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
    if actual_thread_id:
        for elem in result["elements"]:
            if elem.get("type") == "DfElement":
                df_id = elem.get("df_id") or elem.get("block_id")
                if df_id:
                    # Fetch the actual dataframe via Arrow
                    df = client._fetch_dataframe_arrow(actual_thread_id, df_id)
                    if df is not None:
                        elem["table"] = df

    return result
