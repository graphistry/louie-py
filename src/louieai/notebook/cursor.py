"""Global cursor implementation for notebook-friendly API."""

import logging
from collections import deque
from typing import Any

import pandas as pd

from louieai._client import LouieClient, Response

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
        # Process all elements in order
        if hasattr(response, "elements") and response.elements:
            for elem in response.elements:
                if not isinstance(elem, dict):
                    continue

                elem_type = elem.get("type", "")

                # TextElement
                if elem_type in ["TextElement", "text"]:
                    # Handle both old and new field names
                    content = (
                        elem.get("content")
                        or elem.get("text", "")
                        or elem.get("value", "")
                    ).strip()
                    if content:
                        # Use IPython's Markdown renderer for consistency
                        try:
                            from IPython.display import Markdown

                            md = Markdown(content)
                            # Get the actual markdown-rendered HTML
                            from IPython.core.formatters import HTMLFormatter

                            formatter = HTMLFormatter()
                            html_content = formatter(md)
                            if html_content:
                                html_parts.append(html_content)
                            else:
                                # Fallback: basic markdown-like conversion
                                import html

                                escaped = html.escape(content)
                                # Basic markdown-like formatting
                                escaped = escaped.replace("\n\n", "</p><p>")
                                escaped = escaped.replace("\n", "<br>")
                                if escaped.startswith("## "):
                                    escaped = f"<h2>{escaped[3:]}</h2>"
                                elif escaped.startswith("# "):
                                    escaped = f"<h1>{escaped[2:]}</h1>"
                                html_parts.append(f"<div>{escaped}</div>")
                        except ImportError:
                            # No IPython, use basic HTML
                            import html

                            escaped = html.escape(content).replace("\n", "<br>")
                            html_parts.append(f"<div>{escaped}</div>")

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
                            f"font-size: 0.9em;'>🐛 {text}</div>"
                        )

                # InfoLine
                elif elem_type == "InfoLine":
                    text = elem.get("text", "")
                    if text:
                        html_parts.append(
                            f"<div style='color: #0066cc; font-family: monospace; "
                            f"font-size: 0.9em;'>i {text}</div>"
                        )

                # WarningLine
                elif elem_type == "WarningLine":
                    text = elem.get("text", "")
                    if text:
                        html_parts.append(
                            f"<div style='color: #ff8800; font-family: monospace; "
                            f"font-size: 0.9em;'>⚠️ {text}</div>"
                        )

                # ErrorLine
                elif elem_type == "ErrorLine":
                    text = elem.get("text", "")
                    if text:
                        html_parts.append(
                            f"<div style='color: #cc0000; font-family: monospace; "
                            f"font-size: 0.9em;'>❌ {text}</div>"
                        )

                # ExceptionElement
                elif elem_type == "ExceptionElement":
                    msg = elem.get("message", "Unknown error")
                    html_parts.append(
                        f"<div style='color: red; background: #ffe0e0; padding: 10px; "
                        f"margin: 5px 0;'>⚠️ Error: {msg}</div>"
                    )

                # CodeElement
                elif elem_type == "CodeElement":
                    code = elem.get("code", "") or elem.get("text", "")
                    if code:
                        html_parts.append(
                            f"<pre style='background: #f5f5f5; padding: 10px; "
                            f"border-radius: 5px;'><code>{code}</code></pre>"
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

                    if dataset_id:
                        # Create iframe for Graphistry visualization
                        iframe_url = (
                            f"{server_url}/graph/graph.html?dataset={dataset_id}"
                        )
                        html_parts.append(
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
                        html_parts.append(
                            f"<div style='color: gray;'>[{elem_type}] {text}</div>"
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
        """Primary text or None."""
        texts = self.texts
        return texts[-1] if texts else None

    @property
    def texts(self) -> list[str]:
        """All text elements."""
        if not self._response:
            return []
        if (
            not hasattr(self._response, "text_elements")
            or not self._response.text_elements
        ):
            return []
        # Handle 'content', 'text', and 'value' keys for backward compatibility
        return [
            elem.get("content") or elem.get("text", "") or elem.get("value", "")
            for elem in self._response.text_elements
        ]

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

        # If response has raw elements list, check for ExceptionElements
        if hasattr(self._response, "elements") and self._response.elements:
            for elem in self._response.elements:
                if isinstance(elem, dict) and elem.get("type") == "ExceptionElement":
                    result.append(
                        {
                            "type": "error",
                            "value": elem.get("message", "Unknown error"),
                            "error_type": elem.get("error_type"),
                            "traceback": elem.get("traceback"),
                        }
                    )

        # Add text elements
        if hasattr(self._response, "text_elements") and self._response.text_elements:
            for elem in self._response.text_elements:
                if isinstance(elem, dict):
                    # Check 'content', 'text', and 'value' keys for backward
                    # compatibility
                    value = (
                        elem.get("content")
                        or elem.get("text", "")
                        or elem.get("value", "")
                    )
                    result.append({"type": "text", "value": value})

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
        if not hasattr(self._response, "elements"):
            return []
        return [
            elem
            for elem in self._response.elements
            if isinstance(elem, dict) and elem.get("type") == "ExceptionElement"
        ]

    @property
    def has_errors(self) -> bool:
        """Check if response contains errors."""
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
        >>> lui.traces = True  # Enable reasoning traces
        >>> lui("Complex query", traces=False)  # Override per query

    Data Access:
        - lui.df: Latest dataframe (or None)
        - lui.dfs: All dataframes from latest response
        - lui.g: Latest graph element (or None)
        - lui.gs: All graph elements from latest response
        - lui.text: Primary text response
        - lui.texts: All text elements
        - lui.elements: All elements with type tags
    """

    def __init__(
        self,
        client: LouieClient | None = None,
        share_mode: str = "Private",
        name: str | None = None,
    ):
        """Initialize global cursor.

        Args:
            client: LouieAI client instance. If None, creates default client.
            share_mode: Default visibility mode - "Private", "Organization", or "Public"
            name: Optional thread name (auto-generated from first message if not
                provided)
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
        self._share_mode: str = share_mode
        self._name: str | None = name
        self._last_display_id: str | None = None

    def __call__(
        self,
        prompt: str | pd.DataFrame,
        df: pd.DataFrame | None = None,
        *,
        traces: bool | None = None,
        share_mode: str | None = None,
        **kwargs: Any,
    ) -> "Cursor":
        """Execute a query with implicit thread management and optional DataFrame.

        Supports upload of pandas DataFrames for AI-powered analysis.

        Supports flexible calling patterns for both text queries and DataFrame analysis.
        Thread management is automatic - continues current thread or starts new.

        Args:
            prompt: Natural language query string, or DataFrame if using reversed syntax
            df: Optional pandas DataFrame to upload and analyze with the query
            traces: Override session trace setting for this query (shows AI reasoning)
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

        # Determine trace setting
        use_traces = traces if traces is not None else self._traces

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
                    share_mode=use_share_mode,
                    name=self._name,
                    format=kwargs.get("format", "parquet"),
                    parsing_options=kwargs.get("parsing_options"),
                )
            elif actual_image is not None:
                # Use upload_image for image queries
                response = self._client.upload_image(
                    prompt=actual_prompt,
                    image=actual_image,
                    thread_id=thread_id,
                    agent=agent,
                    traces=use_traces,
                    share_mode=use_share_mode,
                    name=self._name,
                )
            elif actual_binary is not None:
                # Use upload_binary for binary file queries
                response = self._client.upload_binary(
                    prompt=actual_prompt,
                    file=actual_binary,
                    thread_id=thread_id,
                    agent=agent,
                    traces=use_traces,
                    share_mode=use_share_mode,
                    name=self._name,
                    filename=kwargs.get("filename"),
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
                    share_mode=use_share_mode,
                )

                # Create Response object from streaming result
                from .._client import Response

                response = Response(
                    thread_id=result["dthread_id"], elements=result["elements"]
                )
            else:
                # Non-Jupyter or updating existing display
                response = self._client.add_cell(
                    thread_id=thread_id,
                    prompt=actual_prompt,
                    agent=agent,
                    traces=use_traces,
                    share_mode=use_share_mode,
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
        """Check if running in Jupyter environment."""
        try:
            # Check for IPython without importing it
            import sys

            return "IPython" in sys.modules
        except Exception:
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
        """Get trace setting for this session."""
        return self._traces

    @traces.setter
    def traces(self, value: bool) -> None:
        """Set trace setting for this session."""
        self._traces = value

    @property
    def thread_id(self) -> str | None:
        """Get the current thread ID."""
        return self._current_thread

    @property
    def url(self) -> str | None:
        """Get the URL for the current thread.

        Returns a shareable URL that opens the current conversation thread
        in the Louie web interface. Useful for sharing analysis results
        with team members or bookmarking conversations.

        Returns:
            str | None: The thread URL if a thread exists, None otherwise.

        Example:
            >>> lui("Analyze customer churn patterns")
            >>> print(f"Share this analysis: {lui.url}")
            Share this analysis: https://den.louie.ai/?dthread=abc123...
        """
        if not self._current_thread:
            return None
        base_url = self._client.server_url.rstrip("/")
        return f"{base_url}/?dthread={self._current_thread}"

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
        """Primary text or None."""
        texts = self.texts
        return texts[-1] if texts else None

    @property
    def texts(self) -> list[str]:
        """All text elements."""
        if not self._history:
            return []
        latest = self._history[-1]
        if not hasattr(latest, "text_elements") or not latest.text_elements:
            return []
        # Handle both 'content' and 'text' keys for backward compatibility
        return [
            elem.get("content") or elem.get("text", "") for elem in latest.text_elements
        ]

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
        return len(self.errors) > 0

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

        # Traces info
        status_parts.append(f"Traces: {'Enabled' if self._traces else 'Disabled'}")

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
                "🔍 <b>Traces:</b> Enabled (showing AI reasoning)</p>"
            )
        else:
            html_parts.append(
                "<p style='margin: 5px 0; font-size: 0.9em;'>"
                "🔍 <b>Traces:</b> Disabled "
                "(use <code>lui.traces = True</code> to enable)</p>"
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
                    html_parts.append(f"<li>{msg}</li>")
                if len(proxy.errors) > 3:
                    html_parts.append(
                        f"<li>... and {len(proxy.errors) - 3} more errors</li>"
                    )
                html_parts.append("</ul>")
                html_parts.append("<p>Access errors with <code>lui.errors</code></p>")
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
        html_parts.append("# Traces (AI reasoning)\n")
        html_parts.append("lui.traces = True    # Enable for session\n")
        html_parts.append("lui('query', traces=True)  # Enable for one query")
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

    def new(self, share_mode: str | None = None, name: str | None = None) -> "Cursor":
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
        return Cursor(
            client=self._client,  # Pass entire authenticated client instance
            share_mode=share_mode,
            name=name,
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
