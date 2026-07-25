"""Global cursor implementation for notebook-friendly API."""

import html
import logging
from collections import deque
from typing import Any

import pandas as pd

from louieai._client import LouieClient, Response
from louieai._tracing import generate_trace_id
from louieai._types import ShareMode, UserAgent

from ._html import graph_url

logger = logging.getLogger(__name__)


def _render_response_html(response, client=None) -> str:
    """Render response to HTML - shared by both auto-display and ResponseProxy.

    This is the single source of truth for response rendering.

    Args:
        response: Response object to render
        client: Optional LouieClient instance for accessing Graphistry settings
    """
    if not response:
        return ""

    html_parts = []

    try:
        status = getattr(response, "status", None)
        if isinstance(status, str) and status != "unknown":
            html_parts.append(
                "<div style=.font-size: 0.9em; margin-bottom: 8px;.>"
                f"<b>Status:</b> {html.escape(status)}</div>"
            )

        terminal_error = getattr(response, "terminal_error", None)
        if isinstance(terminal_error, str) and terminal_error:
            html_parts.append(
                "<div style=.color: #d73a49; margin-bottom: 8px;.>"
                f"<b>Error:</b> {html.escape(terminal_error)}</div>"
            )

        phases = getattr(response, "phases", None)
        if isinstance(phases, list) and phases:
            html_parts.append("<details><summary><b>Execution phases</b></summary><ul>")
            for phase in phases:
                if not isinstance(phase, dict):
                    continue
                action = phase.get("action")
                expression = (
                    action.get("expression") if isinstance(action, dict) else None
                )
                label = (
                    expression or phase.get("run_type") or phase.get("id") or "phase"
                )
                state = phase.get("state", "unknown")
                html_parts.append(
                    f"<li>{html.escape(str(label))}: {html.escape(str(state))}</li>"
                )
            html_parts.append("</ul></details>")

        reasoning = getattr(response, "reasoning_elements", None)
        reasoning_ids = (
            {
                str(element.get("id"))
                for element in reasoning
                if isinstance(element, dict) and element.get("id") is not None
            }
            if isinstance(reasoning, list)
            else set()
        )

        # Process all elements in order
        if hasattr(response, "elements") and response.elements:
            for elem in response.elements:
                if not isinstance(elem, dict):
                    continue

                elem_type = elem.get("type", "")

                # TextElement
                if elem_type in ["TextElement", "text"]:
                    content_value = (
                        elem.get("content")
                        or elem.get("text", "")
                        or elem.get("value", "")
                    )
                    content = str(content_value).strip()
                    if content:
                        safe_content = html.escape(content, quote=False)
                        try:
                            from IPython.core.formatters import HTMLFormatter
                            from IPython.display import Markdown

                            formatter = HTMLFormatter()
                            rendered = formatter(Markdown(safe_content))
                            if not rendered:
                                rendered = safe_content.replace("\n", "<br>")
                        except ImportError:
                            rendered = safe_content.replace("\n", "<br>")

                        if str(elem.get("id")) in reasoning_ids:
                            html_parts.append(
                                "<details style='margin: 5px 0;'>"
                                "<summary><b>Reasoning</b></summary>"
                                f"<div>{rendered}</div></details>"
                            )
                        else:
                            html_parts.append(f"<div>{rendered}</div>")

                # DfElement
                elif elem_type in ["DfElement", "df"] and "table" in elem:
                    df = elem["table"]
                    if hasattr(df, "_repr_html_"):
                        df_html = df._repr_html_()
                        if df_html:
                            html_parts.append(df_html)

                # DebugLine
                elif elem_type == "DebugLine":
                    text = elem.get("text", "")
                    if text:
                        html_parts.append(
                            f"<div style='color: #666; font-family: monospace; "
                            f"font-size: 0.9em;'>🐛 {html.escape(str(text))}</div>"
                        )

                # InfoLine
                elif elem_type == "InfoLine":
                    text = elem.get("text", "")
                    if text:
                        html_parts.append(
                            f"<div style='color: #0066cc; font-family: monospace; "
                            f"font-size: 0.9em;'>i {html.escape(str(text))}</div>"
                        )

                # WarningLine
                elif elem_type == "WarningLine":
                    text = elem.get("text", "")
                    if text:
                        html_parts.append(
                            f"<div style='color: #ff8800; font-family: monospace; "
                            f"font-size: 0.9em;'>⚠️ {html.escape(str(text))}</div>"
                        )

                # ErrorLine
                elif elem_type == "ErrorLine":
                    text = elem.get("text", "")
                    if text:
                        html_parts.append(
                            f"<div style='color: #cc0000; font-family: monospace; "
                            f"font-size: 0.9em;'>❌ {html.escape(str(text))}</div>"
                        )

                # ExceptionElement
                elif elem_type == "ExceptionElement":
                    msg = elem.get("message", "Unknown error")
                    html_parts.append(
                        f"<div style='color: red; background: #ffe0e0; padding: 10px; "
                        f"margin: 5px 0;'>⚠️ Error: {html.escape(str(msg))}</div>"
                    )

                # CodeElement
                elif elem_type == "CodeElement":
                    code = elem.get("code", "") or elem.get("text", "")
                    if code:
                        safe_code = html.escape(str(code), quote=False)
                        html_parts.append(
                            f"<pre style='background: #f5f5f5; padding: 10px; "
                            f"border-radius: 5px;'><code>{safe_code}</code></pre>"
                        )

                # GraphElement
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

                    # Check for code content (for generated graphs like hypergraph)
                    if not dataset_id:
                        # Try to get code from text or code field
                        elem.get("text") or elem.get("code")

                    # Get Graphistry server URL from client if available
                    server_url = "https://hub.graphistry.com"  # default
                    if client and hasattr(client, "_auth_manager"):
                        try:
                            g = client._auth_manager._graphistry_client
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

                    iframe_url = graph_url(server_url, dataset_id)
                    if iframe_url:
                        safe_iframe_url = html.escape(iframe_url, quote=True)
                        html_parts.append(
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
                        html_parts.append(
                            f"<div style='color: #888; padding: 10px; "
                            f"background: #f5f5f5; margin: 5px 0;'>"
                            f"[{elem_type}] Graph visualization not available</div>"
                        )

                # Unknown types - try to extract text
                else:
                    text = (
                        elem.get("text", "")
                        or elem.get("content", "")
                        or str(elem.get("value", ""))
                    )
                    if text:
                        safe_type = html.escape(str(elem_type))
                        html_parts.append(
                            f"<div style='color: gray;'>[{safe_type}] "
                            f"{html.escape(str(text))}</div>"
                        )

    except Exception:
        # Fallback on any error
        html_parts.append(
            "<div style='color: #888;'><em>Response content unavailable</em></div>"
        )

    return "\n".join(html_parts)


class ResponseProxy:
    """Proxy for historical responses with same property access."""

    def __init__(self, response: Response | None):
        self._response = response

    @property
    def response(self) -> Response | None:
        """Underlying raw response, if available."""
        return self._response

    def _list_property(self, name: str) -> list[Any]:
        if not self._response:
            return []
        value = getattr(self._response, name, None)
        return value if isinstance(value, list) else []

    @property
    def stream_messages(self) -> list[dict[str, Any]]:
        """Ordered raw stream envelopes."""
        return self._list_property("stream_messages")

    @property
    def run_updates(self) -> list[dict[str, Any]]:
        """Ordered root and method run snapshots."""
        return self._list_property("run_updates")

    @property
    def phase_updates(self) -> list[dict[str, Any]]:
        """Ordered method-run phase snapshots."""
        return self._list_property("phase_updates")

    @property
    def phases(self) -> list[dict[str, Any]]:
        """Latest snapshot for each execution phase."""
        return self._list_property("phases")

    @property
    def root_run(self) -> dict[str, Any] | None:
        """Latest root-run snapshot."""
        value = getattr(self._response, "root_run", None) if self._response else None
        return value if isinstance(value, dict) else None

    @property
    def status(self) -> str:
        """Normalized execution status."""
        value = getattr(self._response, "status", None) if self._response else None
        return value if isinstance(value, str) else "unknown"

    @property
    def token_flow(self) -> dict[str, Any] | None:
        """Latest root-run token counters."""
        value = getattr(self._response, "token_flow", None) if self._response else None
        return value if isinstance(value, dict) else None

    @property
    def trace_events(self) -> list[Any]:
        """Returned server trace payloads; distinct from the traces request bool."""
        return self._list_property("trace_events")

    @property
    def terminal(self) -> dict[str, Any] | None:
        """Final terminal stream envelope."""
        value = getattr(self._response, "terminal", None) if self._response else None
        return value if isinstance(value, dict) else None

    @property
    def terminal_error(self) -> str | None:
        """Final terminal error message."""
        value = (
            getattr(self._response, "terminal_error", None) if self._response else None
        )
        return value if isinstance(value, str) else None

    @property
    def succeeded(self) -> bool | None:
        """Final stream success flag."""
        value = getattr(self._response, "succeeded", None) if self._response else None
        return value if isinstance(value, bool) else None

    @property
    def reasoning_elements(self) -> list[dict[str, Any]]:
        """Latest text snapshots classified as reasoning."""
        return self._list_property("reasoning_elements")

    @property
    def reasoning_texts(self) -> list[str]:
        """Reasoning text parts."""
        return self._list_property("reasoning_texts")

    @property
    def reasoning_text(self) -> str | None:
        """Joined reasoning text."""
        value = (
            getattr(self._response, "reasoning_text", None) if self._response else None
        )
        return value if isinstance(value, str) else None

    @property
    def final_text_elements(self) -> list[dict[str, Any]]:
        """Non-reasoning text output elements."""
        if not self._response:
            return []
        value = getattr(self._response, "final_text_elements", None)
        if isinstance(value, list):
            return value
        value = getattr(self._response, "text_elements", None)
        return value if isinstance(value, list) else []

    @property
    def final_texts(self) -> list[str]:
        """Non-reasoning text outputs."""
        if self._response:
            value = getattr(self._response, "final_texts", None)
            if isinstance(value, list):
                return value
        return [
            elem.get("content") or elem.get("text", "") or elem.get("value", "")
            for elem in self.final_text_elements
        ]

    @property
    def final_text(self) -> str | None:
        """Explicit final answer, with latest-text fallback for legacy responses."""
        if self._response:
            value = getattr(self._response, "final_text", None)
            if isinstance(value, str) or value is None:
                return value
        texts = self.final_texts
        return texts[-1] if texts else None

    @property
    def df(self) -> pd.DataFrame | None:
        """Latest dataframe or None."""
        dfs = self.dfs
        return dfs[-1] if dfs else None

    @property
    def dfs(self) -> list[pd.DataFrame]:
        """All dataframes from this response."""
        if not self._response:
            return []
        return self._extract_dataframes(self._response)

    @property
    def df_id(self) -> str | None:
        """ID of the latest dataframe or None."""
        if not self._response:
            return None
        if (
            not hasattr(self._response, "dataframe_elements")
            or not self._response.dataframe_elements
        ):
            return None
        # Get the last DataFrame element's ID
        for elem in reversed(self._response.dataframe_elements):
            if isinstance(elem, dict):
                # Try df_id, then block_id, then id
                df_id = elem.get("df_id") or elem.get("block_id") or elem.get("id")
                if df_id:
                    return str(df_id)
        return None

    @property
    def df_ids(self) -> list[str]:
        """All dataframe IDs from this response."""
        if not self._response:
            return []
        if (
            not hasattr(self._response, "dataframe_elements")
            or not self._response.dataframe_elements
        ):
            return []
        ids = []
        for elem in self._response.dataframe_elements:
            if isinstance(elem, dict):
                df_id = elem.get("df_id") or elem.get("block_id") or elem.get("id")
                if df_id:
                    ids.append(str(df_id))
        return ids

    @property
    def text(self) -> str | None:
        """Primary final-oriented text or None."""
        return self.final_text

    @property
    def texts(self) -> list[str]:
        """All non-reasoning text outputs."""
        return self.final_texts

    @property
    def g(self) -> dict[str, Any] | None:
        """Latest graph element or None."""
        gs = self.gs
        return gs[-1] if gs else None

    @property
    def gs(self) -> list[dict[str, Any]]:
        """All graph elements from this response."""
        if not self._response:
            return []

        # Use the graph_elements property which already filters elements
        if hasattr(self._response, "graph_elements"):
            return self._response.graph_elements

        return []

    @property
    def elements(self) -> list[dict[str, Any]]:
        """All elements with type tags."""
        if not self._response:
            return []

        result = []

        for elem in self.errors:
            result.append(
                {
                    "type": "error",
                    "value": elem.get("message", "Unknown error"),
                    "error_type": elem.get("error_type"),
                    "traceback": elem.get("traceback"),
                }
            )

        for elem in self.final_text_elements:
            value = elem.get("content") or elem.get("text", "") or elem.get("value", "")
            result.append({"type": "text", "value": value})

        for elem in self.reasoning_elements:
            value = elem.get("content") or elem.get("text", "") or elem.get("value", "")
            result.append({"type": "reasoning", "value": value})

        # Add dataframe elements
        if (
            hasattr(self._response, "dataframe_elements")
            and self._response.dataframe_elements
        ):
            for elem in self._response.dataframe_elements:
                if isinstance(elem, dict) and "table" in elem:
                    df_element = {
                        "type": "dataframe",
                        "value": elem["table"],  # Backward compatibility
                        "df": elem["table"],  # Convenient access as 'df'
                    }
                    # Include metadata from the original element
                    for key in ["id", "df_id", "block_id"]:
                        if key in elem:
                            df_element[key] = elem[key]
                    result.append(df_element)

        # Add graph elements
        if hasattr(self._response, "graph_elements") and self._response.graph_elements:
            for elem in self._response.graph_elements:
                result.append({"type": "graph", "value": elem})

        return result

    @property
    def errors(self) -> list[dict[str, Any]]:
        """All error elements."""
        if not self._response:
            return []
        response_errors = getattr(self._response, "errors", None)
        if isinstance(response_errors, list):
            return [elem for elem in response_errors if isinstance(elem, dict)]
        if not hasattr(self._response, "elements"):
            return []
        return [
            elem
            for elem in self._response.elements
            if isinstance(elem, dict)
            and elem.get("type") in {"ExceptionElement", "exception", "error"}
        ]

    @property
    def has_errors(self) -> bool:
        """Check if response contains errors."""
        if self._response and hasattr(self._response, "has_errors"):
            value = self._response.has_errors
            if isinstance(value, bool):
                return value
        return len(self.errors) > 0

    def _extract_dataframes(self, response: Response) -> list[pd.DataFrame]:
        """Extract pandas DataFrames from response."""
        if (
            not hasattr(response, "dataframe_elements")
            or not response.dataframe_elements
        ):
            return []
        dfs = []
        for elem in response.dataframe_elements:
            if (
                isinstance(elem, dict)
                and "table" in elem
                and isinstance(elem["table"], pd.DataFrame)
            ):
                dfs.append(elem["table"])
        return dfs

    def __repr__(self) -> str:
        """String representation for REPL/notebook display."""
        if not self._response:
            return "<ResponseProxy: No response>"

        # Count content
        text_count = len(self.texts)
        df_count = len(self.dfs)
        error_count = len(self.errors)

        parts = []
        if error_count:
            parts.append(f"{error_count} errors")
        if text_count:
            parts.append(f"{text_count} text")
        if df_count:
            parts.append(f"{df_count} dataframe")

        if parts:
            content = ", ".join(parts)
            return f"<ResponseProxy: {content}>"
        else:
            return "<ResponseProxy: Empty response>"

    def _repr_html_(self) -> str:
        """HTML representation for Jupyter notebooks - identical to auto-display."""
        if not self._response:
            return "<div style='color: #888;'><em>No response data</em></div>"

        # Use the shared renderer to ensure lui('query') and lui[-1] show identical
        # content
        html_content = _render_response_html(self._response)

        return (
            html_content
            if html_content
            else "<div style='color: #888;'><em>Empty response</em></div>"
        )


class Cursor:
    """Cursor for natural language queries and DataFrame analysis.

    Provides implicit thread management, history tracking, and DataFrame upload
    capabilities for natural notebook workflows with AI-powered data analysis.

    Quick Start:
        >>> import louieai as lui
        >>> lui("What's the weather today?")
        >>> lui.df  # Access any returned dataframe
        >>> lui.text  # Access the text response

    DataFrame Analysis:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> lui("Calculate correlation", df)  # Upload and analyze
        >>> lui(df, "sum")  # Reversed syntax for simple operations
        >>> print(lui.text)  # See AI's analysis

    Session Management:
        - Thread ID managed automatically
        - History tracked (last 100 responses)
        - Access previous: lui[-1], lui[-2], etc.

    Visibility Control:
        >>> lui = louieai(share_mode="Organization")  # Set default for session
        >>> lui("Query")  # Uses Organization visibility
        >>> lui("Query", share_mode="Private")  # Override for this query

    Trace Control:
        >>> lui.traces = True  # Request server trace events
        >>> lui("Complex query", traces=False)  # Override per query

    Reasoning Control:
        >>> lui.include_reasoning = True  # Include provisional reasoning
        >>> lui("Query", include_reasoning=False)  # Override per query

    Data Access:
        - lui.df: Latest dataframe (or None)
        - lui.dfs: All dataframes from latest response
        - lui.g: Latest graph element (or None)
        - lui.gs: All graph elements from latest response
        - lui.text: Primary text response
        - lui.texts: All non-reasoning text outputs
        - lui.reasoning_text: Opt-in provisional reasoning
        - lui.phases: Latest execution phase snapshots
        - lui.elements: All elements with type tags
    """

    def __init__(
        self,
        client: LouieClient | None = None,
        share_mode: ShareMode = "Private",
        name: str | None = None,
        folder: str | None = None,
        user_agent: UserAgent = "API",
        frontend_url: str | None = None,
        _parent_trace_id: str | None = None,
        *,
        include_reasoning: bool = False,
    ):
        """Initialize global cursor.

        Args:
            client: LouieAI client instance. If None, creates default client.
            share_mode: Default visibility mode - "Private", "Organization", or "Public"
            name: Optional thread name (auto-generated from first message if not
                provided)
            folder: Optional folder path for new threads (server support required)
            user_agent: DataThread creation_user_agent — "API" or "Louie"
            frontend_url: Override base URL for thread links. Auto-detected
                if not set: localhost → ``louie://n/`` deep links, remote →
                ``server_url``. Devs running a team server on localhost can
                pass e.g. ``frontend_url="http://localhost:5173"``.
            _parent_trace_id: Internal parameter for inheriting trace context from
                parent cursor. Do not use directly.
            include_reasoning: Include provisional reasoning by default for this
                Cursor. Can be overridden per query.
        """
        # Validate share_mode
        valid_modes = {"Private", "Organization", "Public"}
        if share_mode not in valid_modes:
            raise ValueError(
                f"Invalid share_mode: '{share_mode}'. "
                f"Must be one of: {', '.join(sorted(valid_modes))}"
            )

        if client is None:
            # Create client with env credentials if available
            import os

            # Check for Louie-specific URL
            server_url = os.environ.get("LOUIE_URL", "https://den.louie.ai")

            # Check for credentials - support multiple auth methods
            # 1. Personal key authentication (PyGraphistry service accounts)
            personal_key_id = os.environ.get("GRAPHISTRY_PERSONAL_KEY_ID")
            personal_key_secret = os.environ.get("GRAPHISTRY_PERSONAL_KEY_SECRET")

            # 2. API key authentication (legacy)
            api_key = os.environ.get("GRAPHISTRY_API_KEY")

            # 3. Username/password authentication
            username = os.environ.get("GRAPHISTRY_USERNAME")
            password = os.environ.get("GRAPHISTRY_PASSWORD")

            # 4. Organization name (optional for all auth methods)
            org_name = os.environ.get("GRAPHISTRY_ORG_NAME")

            # 5. Server configuration
            server = os.environ.get("GRAPHISTRY_SERVER")

            # 6. Timeout configuration
            timeout_str = os.environ.get("LOUIE_TIMEOUT", "300")
            streaming_timeout_str = os.environ.get("LOUIE_STREAMING_TIMEOUT", "120")
            try:
                timeout = float(timeout_str)
            except ValueError:
                timeout = 300.0
            try:
                streaming_timeout = float(streaming_timeout_str)
            except ValueError:
                streaming_timeout = 120.0

            # Build client kwargs
            client_kwargs: dict[str, Any] = {
                "server_url": server_url,
                "timeout": timeout,
                "streaming_timeout": streaming_timeout,
            }

            # Add all available authentication parameters
            # The LouieClient will handle priority internally
            if personal_key_id:
                client_kwargs["personal_key_id"] = personal_key_id
            if personal_key_secret:
                client_kwargs["personal_key_secret"] = personal_key_secret
            if api_key:
                client_kwargs["api_key"] = api_key
            if username:
                client_kwargs["username"] = username
            if password:
                client_kwargs["password"] = password
            if org_name:
                client_kwargs["org_name"] = org_name
            if server:
                client_kwargs["server"] = server

            client = LouieClient(**client_kwargs)
        self._client = client
        self._history: deque[Response] = deque(maxlen=100)
        self._current_thread: str | None = None
        self._traces: bool = False
        self._include_reasoning: bool = include_reasoning
        self._share_mode: ShareMode = share_mode
        self._name: str | None = name
        self._folder: str | None = folder
        self._user_agent: UserAgent = user_agent
        self._frontend_url: str | None = frontend_url
        self._last_display_id: str | None = None
        # Session-level trace ID for correlating requests when OTel is not available
        self._trace_id: str = _parent_trace_id or generate_trace_id()

    def __call__(
        self,
        prompt: str | pd.DataFrame,
        df: pd.DataFrame | None = None,
        *,
        traces: bool | None = None,
        include_reasoning: bool | None = None,
        share_mode: ShareMode | None = None,
        **kwargs: Any,
    ) -> "Cursor":
        """Execute a query with implicit thread management and optional DataFrame.

        Supports upload of pandas DataFrames for AI-powered analysis.

        Supports flexible calling patterns for both text queries and DataFrame analysis.
        Thread management is automatic - continues current thread or starts new.

        Args:
            prompt: Natural language query string, or DataFrame if using reversed syntax
            df: Optional pandas DataFrame to upload and analyze with the query
            traces: Override whether server trace events are requested.
            include_reasoning: Override whether provisional reasoning text is returned.
            share_mode: Override default visibility for this query:
                - "Private": Only you can see it
                - "Organization": Visible to your organization
                - "Public": Publicly accessible
            **kwargs: Additional arguments for upload_dataframe() when df is provided:
                - format: "parquet" (default), "csv", "json", "jsonl", or "arrow"
                - agent: "UploadPassthroughAgent" (default) or "UploadAgent"
                - parsing_options: Dict of format-specific parsing configuration

        Returns:
            Self (Cursor) for chaining and property access:
                - .text: Primary text response
                - .df: Latest DataFrame result
                - .dfs: All DataFrames from response
                - .g: Latest graph visualization
                - .elements: All response elements

        Examples:
            Simple query:
            >>> lui("What is the capital of France?")
            >>> print(lui.text)

            DataFrame analysis (both patterns work):
            >>> import pandas as pd
            >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
            >>>
            >>> # Pattern 1: prompt first
            >>> lui("Calculate the correlation", df)
            >>>
            >>> # Pattern 2: DataFrame first (more natural for simple operations)
            >>> lui(df, "Calculate the correlation")
            >>>
            >>> # Ultra-concise for simple operations
            >>> lui("sum", df)  # Or lui(df, "sum")

            Time series analysis:
            >>> df = pd.DataFrame({
            ...     "date": pd.date_range("2024-01-01", periods=100),
            ...     "sales": np.random.randn(100).cumsum() + 100
            ... })
            >>> lui("Identify trends and forecast next 10 days", df)
            >>> forecast_df = lui.df  # Access returned forecast

            Multi-step analysis in same thread:
            >>> # First upload and analyze
            >>> lui("Summarize this dataset", sales_df)
            >>>
            >>> # Follow-up questions use same thread automatically
            >>> lui("Which products are underperforming?")
            >>>
            >>> # Add more data to the analysis
            >>> lui("Compare with this year's data", sales_2024_df)

            With upload options:
            >>> lui(
            ...     "Analyze this CSV data",
            ...     df,
            ...     format="csv",
            ...     parsing_options={"delimiter": ";", "decimal": ","}
            ... )

            Control visibility per query:
            >>> lui("Analyze company metrics", df, share_mode="Organization")
        """
        # Detect input type and handle accordingly
        actual_image = None
        actual_binary = None

        # Handle flexible argument patterns
        if isinstance(prompt, pd.DataFrame):
            # Pattern: lui(df, "prompt") - swap arguments
            if isinstance(df, str):
                actual_prompt = df
                actual_df = prompt
            else:
                raise ValueError(
                    "When first argument is DataFrame, second must be a string prompt"
                )
        elif self._is_image_input(prompt):
            # Image as first argument
            if df is None:
                # Pattern: lui(image) - image without prompt
                actual_image = prompt
                actual_prompt = "Analyze this image"
                actual_df = None
            elif isinstance(df, str):
                # Pattern: lui(image, "prompt") - swap arguments
                actual_image = prompt
                actual_prompt = df
                actual_df = None
            else:
                raise ValueError(
                    "When first argument is image, second must be a string "
                    "prompt or None"
                )
        elif self._is_binary_file_input(prompt):
            # Binary file as first argument
            if df is None:
                # Pattern: lui(file) - file without prompt
                actual_binary = prompt
                actual_prompt = "Analyze this file"
                actual_df = None
            elif isinstance(df, str):
                # Pattern: lui(file, "prompt") - swap arguments
                actual_binary = prompt
                actual_prompt = df
                actual_df = None
            else:
                raise ValueError(
                    "When first argument is binary file, second must be a "
                    "string prompt or None"
                )
        elif isinstance(prompt, str):
            # String prompt as first argument
            if df is None:
                # Pattern: lui("prompt") - no additional data
                actual_prompt = prompt
                actual_df = None
            elif isinstance(df, pd.DataFrame):
                # Pattern: lui("prompt", df)
                actual_prompt = prompt
                actual_df = df
            elif self._is_image_input(df):
                # Pattern: lui("prompt", image)
                actual_prompt = prompt
                actual_image = df
                actual_df = None
            elif self._is_binary_file_input(df):
                # Pattern: lui("prompt", file)
                actual_prompt = prompt
                actual_binary = df
                actual_df = None
            else:
                raise ValueError(
                    f"Unsupported second argument type: {type(df)}. "
                    "Expected DataFrame, image, binary file, or None"
                )
        else:
            raise ValueError(
                f"Unsupported first argument type: {type(prompt)}. "
                "Expected string prompt, DataFrame, image, or binary file"
            )
        # Get or create thread
        if self._current_thread is None:
            self._current_thread = self._get_or_create_thread()

            # If we have a name and this is the first message, generate a name
            # from prompt
            if self._name is None:
                # Auto-generate name from first message (first 50 chars)
                self._name = actual_prompt[:50] + (
                    "..." if len(actual_prompt) > 50 else ""
                )

        # Determine trace and reasoning settings
        use_traces = traces if traces is not None else self._traces
        use_reasoning = (
            include_reasoning
            if include_reasoning is not None
            else self._include_reasoning
        )

        # Determine share_mode setting
        use_share_mode = share_mode if share_mode is not None else self._share_mode

        # Build parameters
        params = {"prompt": actual_prompt, "thread_id": self._current_thread, **kwargs}

        # Extract add_cell specific params
        thread_id = params.pop("thread_id")
        agent = params.pop(
            "agent",
            "LouieAgent"
            if actual_df is None and actual_image is None and actual_binary is None
            else "UploadPassthroughAgent",
        )

        # Execute query
        try:
            # Check if we have a DataFrame to upload
            if actual_df is not None:
                # Use upload_dataframe for DataFrame queries
                response = self._client.upload_dataframe(
                    prompt=actual_prompt,
                    df=actual_df,
                    thread_id=thread_id,
                    agent=agent,
                    traces=use_traces,
                    include_reasoning=use_reasoning,
                    share_mode=use_share_mode,
                    name=self._name,
                    folder=self._folder,
                    format=kwargs.get("format", "parquet"),
                    parsing_options=kwargs.get("parsing_options"),
                    session_trace_id=self._trace_id,
                )
            elif actual_image is not None:
                # Use upload_image for image queries
                response = self._client.upload_image(
                    prompt=actual_prompt,
                    image=actual_image,
                    thread_id=thread_id,
                    agent=agent,
                    traces=use_traces,
                    include_reasoning=use_reasoning,
                    share_mode=use_share_mode,
                    name=self._name,
                    folder=self._folder,
                    session_trace_id=self._trace_id,
                )
            elif actual_binary is not None:
                # Use upload_binary for binary file queries
                response = self._client.upload_binary(
                    prompt=actual_prompt,
                    file=actual_binary,
                    thread_id=thread_id,
                    agent=agent,
                    traces=use_traces,
                    include_reasoning=use_reasoning,
                    share_mode=use_share_mode,
                    name=self._name,
                    folder=self._folder,
                    filename=kwargs.get("filename"),
                    session_trace_id=self._trace_id,
                )
            elif self._in_jupyter() and self._last_display_id is None:
                # Use streaming display for better UX (non-DataFrame queries)
                from .streaming import stream_response

                result = stream_response(
                    self._client,
                    thread_id=thread_id,
                    prompt=actual_prompt,
                    agent=agent,
                    traces=use_traces,
                    include_reasoning=use_reasoning,
                    share_mode=use_share_mode,
                    user_agent=self._user_agent,
                    name=self._name,
                    folder=self._folder,
                    session_trace_id=self._trace_id,
                )

                # Create Response object from streaming result
                from .._client import Response

                response = Response(
                    thread_id=result["dthread_id"],
                    elements=result["elements"],
                    stream_messages=result.get("stream_messages", []),
                    include_reasoning=use_reasoning,
                )
            else:
                # Non-Jupyter or updating existing display
                response = self._client.add_cell(
                    thread_id=thread_id,
                    prompt=actual_prompt,
                    agent=agent,
                    name=self._name,
                    folder=self._folder,
                    traces=use_traces,
                    include_reasoning=use_reasoning,
                    share_mode=use_share_mode,
                    user_agent=self._user_agent,
                    session_trace_id=self._trace_id,
                )

            # Update thread ID in case it was created
            if not self._current_thread:
                self._current_thread = response.thread_id

            # Store in history
            self._history.append(response)

            # Auto-display in Jupyter if available (only if not streaming)
            # Streaming handles its own display
            if (
                not (self._in_jupyter() and self._last_display_id is None)
                and self._in_jupyter()
                and kwargs.get("display", True)
            ):
                self._display(response)

            # Return self for chaining and property access
            return self

        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def _get_or_create_thread(self) -> str:
        """Get existing thread or create new one."""
        # Return empty string to create new thread on first add_cell
        return ""

    def _in_jupyter(self) -> bool:
        """Check for an active IPython shell, not merely an imported module."""
        try:
            from IPython.core.getipython import get_ipython

            return get_ipython() is not None
        except (ImportError, AttributeError):
            return False

    def _display(self, response: Response) -> None:
        """Display response in Jupyter using the same renderer as ResponseProxy."""
        try:
            from IPython.display import HTML, display

            # Use the shared rendering function, passing client for Graphistry URL
            html_content = _render_response_html(response, self._client)
            if html_content:
                # Generate a unique display ID for this response
                display_id = f"louie_response_{response.thread_id}_{id(response)}"
                display(HTML(html_content), display_id=display_id)

                # Store display ID for potential updates
                self._last_display_id = display_id

        except ImportError:
            # IPython not available, skip display
            pass
        except Exception:
            # Any other error in display, just skip
            pass

    @property
    def traces(self) -> bool:
        """Get whether server trace events are requested for this session."""
        return self._traces

    @traces.setter
    def traces(self, value: bool) -> None:
        """Set whether server trace events are requested for this session."""
        self._traces = value

    @property
    def include_reasoning(self) -> bool:
        """Get whether provisional reasoning is requested for this session."""
        return self._include_reasoning

    @include_reasoning.setter
    def include_reasoning(self, value: bool) -> None:
        """Set whether provisional reasoning is requested for this session."""
        self._include_reasoning = value

    @property
    def thread_id(self) -> str | None:
        """Get the current thread ID."""
        return self._current_thread

    @property
    def url(self) -> str | None:
        """Get the URL for the current thread.

        Returns a link that opens the current conversation thread.
        Desktop servers (localhost) produce ``louie://`` deep links;
        team servers produce web URLs. Override with ``frontend_url``.

        Returns:
            str | None: The thread URL if a thread exists, None otherwise.

        Example:
            >>> lui("Analyze customer churn patterns")
            >>> print(f"Share this analysis: {lui.url}")
            Share this analysis: https://den.louie.ai/?dthread=abc123...
        """
        if not self._current_thread:
            return None
        # Explicit override (e.g., devs running a team server on localhost)
        if self._frontend_url is not None:
            base = self._frontend_url.rstrip("/")
            if base.startswith("louie://"):
                return f"{base}/{self._current_thread}"
            return f"{base}/?dthread={self._current_thread}"
        # Auto-detect: localhost → desktop deep link, otherwise web URL
        server = self._client.server_url
        if "localhost" in server or "127.0.0.1" in server:
            return f"louie://n/{self._current_thread}"
        return f"{server.rstrip('/')}/?dthread={self._current_thread}"

    @property
    def response(self) -> Response | None:
        """Latest raw Response, including streaming metadata."""
        return self._history[-1] if self._history else None

    @property
    def stream_messages(self) -> list[dict[str, Any]]:
        """Ordered raw stream envelopes from the latest response."""
        return ResponseProxy(self.response).stream_messages

    @property
    def run_updates(self) -> list[dict[str, Any]]:
        """Ordered run snapshots from the latest response."""
        return ResponseProxy(self.response).run_updates

    @property
    def phase_updates(self) -> list[dict[str, Any]]:
        """Ordered method-run phase snapshots from the latest response."""
        return ResponseProxy(self.response).phase_updates

    @property
    def phases(self) -> list[dict[str, Any]]:
        """Latest snapshot for each execution phase."""
        return ResponseProxy(self.response).phases

    @property
    def root_run(self) -> dict[str, Any] | None:
        """Latest root-run snapshot."""
        return ResponseProxy(self.response).root_run

    @property
    def status(self) -> str:
        """Normalized execution status for the latest response."""
        return ResponseProxy(self.response).status

    @property
    def token_flow(self) -> dict[str, Any] | None:
        """Latest root-run token counters."""
        return ResponseProxy(self.response).token_flow

    @property
    def trace_events(self) -> list[Any]:
        """Returned trace events; distinct from the traces request bool."""
        return ResponseProxy(self.response).trace_events

    @property
    def terminal(self) -> dict[str, Any] | None:
        """Final terminal stream envelope."""
        return ResponseProxy(self.response).terminal

    @property
    def terminal_error(self) -> str | None:
        """Final terminal error message."""
        return ResponseProxy(self.response).terminal_error

    @property
    def succeeded(self) -> bool | None:
        """Final stream success flag."""
        return ResponseProxy(self.response).succeeded

    @property
    def reasoning_elements(self) -> list[dict[str, Any]]:
        """Latest text snapshots classified as reasoning."""
        return ResponseProxy(self.response).reasoning_elements

    @property
    def reasoning_texts(self) -> list[str]:
        """Reasoning text parts."""
        return ResponseProxy(self.response).reasoning_texts

    @property
    def reasoning_text(self) -> str | None:
        """Joined reasoning text."""
        return ResponseProxy(self.response).reasoning_text

    @property
    def final_text_elements(self) -> list[dict[str, Any]]:
        """Non-reasoning text output elements."""
        return ResponseProxy(self.response).final_text_elements

    @property
    def final_texts(self) -> list[str]:
        """Non-reasoning text outputs."""
        return ResponseProxy(self.response).final_texts

    @property
    def final_text(self) -> str | None:
        """Explicit final answer, with latest-text fallback for legacy responses."""
        return ResponseProxy(self.response).final_text

    @property
    def df(self) -> pd.DataFrame | None:
        """Latest dataframe or None."""
        dfs = self.dfs
        return dfs[-1] if dfs else None

    @property
    def dfs(self) -> list[pd.DataFrame]:
        """All dataframes from latest response."""
        if not self._history:
            return []
        return self._extract_dataframes(self._history[-1])

    @property
    def df_id(self) -> str | None:
        """ID of the latest dataframe or None."""
        if not self._history:
            return None
        latest = self._history[-1]
        if not hasattr(latest, "dataframe_elements") or not latest.dataframe_elements:
            return None
        # Get the last DataFrame element's ID
        for elem in reversed(latest.dataframe_elements):
            if isinstance(elem, dict):
                # Try df_id, then block_id, then id
                df_id = elem.get("df_id") or elem.get("block_id") or elem.get("id")
                if df_id:
                    return str(df_id)
        return None

    @property
    def df_ids(self) -> list[str]:
        """All dataframe IDs from latest response."""
        if not self._history:
            return []
        latest = self._history[-1]
        if not hasattr(latest, "dataframe_elements") or not latest.dataframe_elements:
            return []
        ids = []
        for elem in latest.dataframe_elements:
            if isinstance(elem, dict):
                df_id = elem.get("df_id") or elem.get("block_id") or elem.get("id")
                if df_id:
                    ids.append(str(df_id))
        return ids

    @property
    def text(self) -> str | None:
        """Primary final-oriented text or None."""
        return ResponseProxy(self.response).text

    @property
    def texts(self) -> list[str]:
        """All non-reasoning text outputs from the latest response."""
        return ResponseProxy(self.response).texts

    @property
    def g(self) -> dict[str, Any] | None:
        """Latest graph element or None."""
        gs = self.gs
        return gs[-1] if gs else None

    @property
    def gs(self) -> list[dict[str, Any]]:
        """All graph elements from latest response."""
        if not self._history:
            return []
        proxy = ResponseProxy(self._history[-1])
        return proxy.gs

    @property
    def charts(self) -> list[dict[str, Any]]:
        """All chart specifications."""
        if not self._history:
            return []
        # For now, return empty as charts aren't implemented yet
        return []

    @property
    def images(self) -> list[Any]:
        """All images."""
        if not self._history:
            return []
        # For now, return empty as images aren't implemented yet
        return []

    @property
    def elements(self) -> list[dict[str, Any]]:
        """All elements with type tags."""
        if not self._history:
            return []

        proxy = ResponseProxy(self._history[-1])
        return proxy.elements

    @property
    def errors(self) -> list[dict[str, Any]]:
        """All error elements from latest response."""
        if not self._history:
            return []
        proxy = ResponseProxy(self._history[-1])
        return proxy.errors

    @property
    def has_errors(self) -> bool:
        """Check if latest response contains errors."""
        return ResponseProxy(self.response).has_errors

    def _is_image_input(self, obj: Any) -> bool:
        """Check if object is an image input.

        Args:
            obj: Object to check

        Returns:
            True if object is an image (file path, bytes, PIL Image, etc.)
        """
        if obj is None:
            return False

        # Check for file path with image extension
        if isinstance(obj, str):
            import os
            from pathlib import Path

            # Check if it's a file path
            if os.path.exists(obj) or Path(obj).suffix.lower() in [
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".bmp",
                ".webp",
                ".svg",
                ".tiff",
                ".ico",
            ]:
                return True

        # Check for bytes (could be image data)
        if isinstance(obj, bytes) and (
            obj.startswith(b"\x89PNG")
            or obj.startswith(b"\xff\xd8\xff")
            or obj.startswith(b"GIF8")
            or obj.startswith(b"BM")
            or (obj.startswith(b"RIFF") and b"WEBP" in obj[:20])
        ):
            return True

        # Check for file-like objects with image names
        if hasattr(obj, "read") and hasattr(obj, "name"):
            name = str(obj.name).lower()
            if any(
                name.endswith(ext)
                for ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]
            ):
                return True

        # Check for PIL Image
        try:
            from PIL import Image

            if isinstance(obj, Image.Image):
                return True
        except ImportError:
            pass

        return False

    def _is_binary_file_input(self, obj: Any) -> bool:
        """Check if object is a binary file input (non-image).

        Args:
            obj: Object to check

        Returns:
            True if object is a binary file (PDF, Office docs, etc.)
        """
        if obj is None:
            return False

        # Check for file path with non-image extensions
        if isinstance(obj, str):
            import os
            from pathlib import Path

            # Check if it's a file path with binary file extensions
            if os.path.exists(obj) or Path(obj).suffix.lower() in [
                ".pdf",
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
                ".ppt",
                ".pptx",
                ".txt",
                ".csv",
                ".json",
                ".jsonl",
                ".xml",
                ".zip",
                ".rar",
                ".7z",
                ".mp3",
                ".mp4",
                ".avi",
                ".mov",
                ".wav",
                ".flac",
            ]:
                return True

        # Check for bytes that are not images
        if isinstance(obj, bytes) and (
            obj.startswith(b"%PDF")
            or obj.startswith(b"PK\x03\x04")
            or obj.startswith(b"{")
            or obj.startswith(b"[")
        ):
            return True

        # Check for file-like objects with non-image names
        if hasattr(obj, "read") and hasattr(obj, "name"):
            name = str(obj.name).lower()
            if any(
                name.endswith(ext)
                for ext in [
                    ".pdf",
                    ".doc",
                    ".docx",
                    ".xls",
                    ".xlsx",
                    ".ppt",
                    ".pptx",
                    ".txt",
                    ".csv",
                    ".json",
                    ".jsonl",
                    ".xml",
                    ".zip",
                ]
            ):
                return True

        return False

    def __repr__(self) -> str:
        """String representation for interactive help."""
        status_parts = []

        # Session info
        if self._current_thread:
            status_parts.append("Session: Active")
        else:
            status_parts.append("Session: Not started")

        # History info
        history_count = len(self._history)
        status_parts.append(f"History: {history_count} responses")

        # Request controls
        status_parts.append(f"Traces: {'Enabled' if self._traces else 'Disabled'}")
        status_parts.append(
            f"Reasoning: {'Enabled' if self._include_reasoning else 'Disabled'}"
        )

        # Latest data info
        if self._history:
            latest = self._history[-1]
            data_info = []

            # Count elements
            text_count = (
                len(latest.text_elements) if hasattr(latest, "text_elements") else 0
            )
            df_count = (
                len(latest.dataframe_elements)
                if hasattr(latest, "dataframe_elements")
                else 0
            )

            if text_count:
                data_info.append(f"{text_count} text")
            if df_count:
                data_info.append(f"{df_count} dataframe")

            if data_info:
                status_parts.append(f"Latest: {', '.join(data_info)}")

        status = " | ".join(status_parts)
        return f"<LouieAI Notebook Interface | {status}>"

    def _repr_html_(self) -> str:
        """HTML representation for Jupyter notebooks."""
        html_parts = [
            (
                "<div style='border: 1px solid #ddd; padding: 10px; "
                "border-radius: 5px; margin-bottom: 10px;'>"
            ),
            "<h4 style='margin-top: 0;'>🤖 LouieAI Session</h4>",
        ]

        # Note: Response content is displayed separately via streaming or _display()
        # This shows only session metadata to avoid double display

        # Session info footer
        html_parts.append("<hr style='margin: 10px 0;'>")

        # Session status with organization info
        if self._current_thread:
            session_info = [
                "<p style='margin: 5px 0; font-size: 0.9em;'>",
                "✅ <b>Session:</b> Active | ",
                f"<b>Thread ID:</b> <code>{self._current_thread}</code> | ",
                f"<a href='{self.url}' target='_blank'>View Thread ↗</a>",
            ]

            # Add organization info if available
            if hasattr(
                self._client._auth_manager, "_credentials"
            ) and self._client._auth_manager._credentials.get("org_name"):
                org_name = self._client._auth_manager._credentials["org_name"]
                session_info.append(f" | <b>Org:</b> {org_name}")

            session_info.append("</p>")
            html_parts.append("".join(session_info))
        else:
            html_parts.append(
                "<p style='margin: 5px 0; font-size: 0.9em;'>"
                "⚪ <b>Session:</b> Not started "
                "(use <code>lui('your query')</code>)</p>"
            )

        # History
        history_count = len(self._history)
        html_parts.append(
            f"<p style='margin: 5px 0; font-size: 0.9em;'>"
            f"📚 <b>History:</b> {history_count} responses"
        )
        if history_count > 0:
            html_parts.append(
                " (access with <code>lui[-1]</code>, <code>lui[-2]</code>, etc.)</p>"
            )
        else:
            html_parts.append("</p>")

        # Traces
        if self._traces:
            html_parts.append(
                "<p style='margin: 5px 0; font-size: 0.9em;'>"
                "🔍 <b>Traces:</b> Enabled (requesting server trace events)</p>"
            )
        else:
            html_parts.append(
                "<p style='margin: 5px 0; font-size: 0.9em;'>"
                "🔍 <b>Traces:</b> Disabled "
                "(use <code>lui.traces = True</code> to request events)</p>"
            )

        if self._include_reasoning:
            html_parts.append(
                "<p style='margin: 5px 0; font-size: 0.9em;'>"
                "🧠 <b>Reasoning:</b> Included for this session</p>"
            )
        else:
            html_parts.append(
                "<p style='margin: 5px 0; font-size: 0.9em;'>"
                "🧠 <b>Reasoning:</b> Final answer only "
                "(use <code>lui.include_reasoning = True</code> to opt in)</p>"
            )

        # Latest data
        if self._history:
            latest = self._history[-1]
            proxy = ResponseProxy(latest)

            # Check for errors first
            if proxy.has_errors:
                html_parts.append("<p>⚠️ <b>Latest Response Contains Errors:</b></p>")
                html_parts.append("<ul style='margin: 5px 0; color: #d73a49;'>")
                for error in proxy.errors[:3]:  # Show first 3 errors
                    msg = error.get("message", "Unknown error")
                    html_parts.append(f"<li>{html.escape(str(msg))}</li>")
                if len(proxy.errors) > 3:
                    html_parts.append(
                        f"<li>... and {len(proxy.errors) - 3} more errors</li>"
                    )
                if not proxy.errors and proxy.terminal_error:
                    html_parts.append(f"<li>{html.escape(proxy.terminal_error)}</li>")
                html_parts.append("</ul>")
                if proxy.errors:
                    html_parts.append(
                        "<p>Access errors with <code>lui.errors</code></p>"
                    )
                else:
                    html_parts.append(
                        "<p>Access the stream error with "
                        "<code>lui.terminal_error</code></p>"
                    )
            else:
                html_parts.append("<p><b>Latest Response:</b></p>")
                html_parts.append("<ul style='margin: 5px 0;'>")

                # Text elements
                text_count = (
                    len(latest.text_elements) if hasattr(latest, "text_elements") else 0
                )
                if text_count:
                    html_parts.append(
                        f"<li>{text_count} text element(s) - access with "
                        "<code>lui.text</code> or <code>lui.texts</code></li>"
                    )

                # DataFrames
                df_count = (
                    len(latest.dataframe_elements)
                    if hasattr(latest, "dataframe_elements")
                    else 0
                )
                if df_count:
                    html_parts.append(
                        f"<li>{df_count} dataframe(s) - access with "
                        "<code>lui.df</code> or <code>lui.dfs</code></li>"
                    )

                html_parts.append("</ul>")

        # Quick help
        html_parts.append(
            "<details><summary><b>Quick Help</b> (click to expand)</summary>"
        )
        html_parts.append(
            "<pre style='margin: 10px 0; padding: 10px; background: #f5f5f5;'>"
        )
        html_parts.append("# Make a query\n")
        html_parts.append("lui('Show me sales data from last week')\n\n")
        html_parts.append("# Control visibility\n")
        html_parts.append(
            "lui('query', share_mode='Private')       # Default: only you\n"
        )
        html_parts.append(
            "lui('query', share_mode='Organization')  # Share within org\n"
        )
        html_parts.append(
            "lui('query', share_mode='Public')        # Share publicly\n\n"
        )
        html_parts.append("# Access results\n")
        html_parts.append("df = lui.df          # Latest dataframe\n")
        html_parts.append("text = lui.text      # Latest text response\n")
        html_parts.append("all_dfs = lui.dfs    # All dataframes\n\n")
        html_parts.append("# History\n")
        html_parts.append("lui[-1].df           # Previous response's dataframe\n\n")
        html_parts.append("# Server trace events\n")
        html_parts.append("lui.traces = True    # Request for session\n")
        html_parts.append("events = lui.trace_events\n\n")
        html_parts.append("# Provisional reasoning (opt in)\n")
        html_parts.append("lui.include_reasoning = True\n")
        html_parts.append("reasoning = lui.reasoning_text")
        html_parts.append("</pre>")
        html_parts.append("</details>")

        html_parts.append("</div>")

        return "\n".join(html_parts)

    def __getitem__(self, index: int) -> ResponseProxy:
        """Access history: lui[-1], lui[-2], etc."""
        if not self._history:
            return ResponseProxy(None)
        try:
            return ResponseProxy(self._history[index])
        except IndexError:
            return ResponseProxy(None)

    def new(
        self,
        share_mode: ShareMode | None = None,
        name: str | None = None,
        folder: str | None = None,
    ) -> "Cursor":
        """Create a new Cursor instance with a fresh thread while preserving config.

        This method creates a new conversation thread but maintains all authentication
        and configuration from the parent cursor, including:
        - The authenticated LouieClient instance with all credentials
        - Server URLs and connection settings
        - Timeout configurations
        - Default agent settings

        Args:
            share_mode: Override visibility mode for new cursor. If None, inherits
                from parent.
            name: Optional thread name for new cursor. Auto-generated from first
                message if not provided.
            folder: Optional folder path for new cursor. If None, inherits from parent.

        Returns:
            Cursor: A new Cursor instance with fresh thread but same configuration

        Examples:
            >>> lui = louie(username="alice", password="<password>",
            ...             share_mode="Organization")
            >>> # Start a new private conversation with same auth
            >>> lui2 = lui.new(share_mode="Private", name="Analysis 2")
            >>> lui2("Analyze different data")  # Uses same credentials but new thread

            >>> # Create another thread inheriting organization visibility
            >>> lui3 = lui.new()  # Inherits share_mode="Organization"
            >>> lui3("Continue analysis")  # Shares within organization
        """
        # Use parent's share_mode if not explicitly provided
        if share_mode is None:
            share_mode = self._share_mode
        else:
            # Validate share_mode if provided
            valid_modes = {"Private", "Organization", "Public"}
            if share_mode not in valid_modes:
                raise ValueError(
                    f"Invalid share_mode: '{share_mode}'. "
                    f"Must be one of: {', '.join(sorted(valid_modes))}"
                )

        # Create new Cursor with same client but fresh thread
        # The client instance contains all auth and configuration
        # Pass parent trace_id so all cursors in same session share a trace
        if folder is None:
            folder = self._folder

        return Cursor(
            client=self._client,  # Pass entire authenticated client instance
            share_mode=share_mode,
            include_reasoning=getattr(self, "_include_reasoning", False),
            name=name,
            folder=folder,
            _parent_trace_id=self._trace_id,  # Share session trace for correlation
        )

    def _extract_dataframes(self, response: Response) -> list[pd.DataFrame]:
        """Extract pandas DataFrames from response."""
        if (
            not hasattr(response, "dataframe_elements")
            or not response.dataframe_elements
        ):
            return []
        dfs = []
        for elem in response.dataframe_elements:
            if (
                isinstance(elem, dict)
                and "table" in elem
                and isinstance(elem["table"], pd.DataFrame)
            ):
                dfs.append(elem["table"])
        return dfs
