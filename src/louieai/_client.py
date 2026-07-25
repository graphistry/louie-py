"""Enhanced Louie client that matches the documented API."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

import httpx
import pandas as pd
import pyarrow as pa

from ._table_ai import (
    TableAIOverrides,
    collect_table_ai_kwargs,
    normalize_table_ai_overrides,
)
from ._tracing import get_traceparent
from ._types import ShareMode, UserAgent
from .auth import AuthManager, auto_retry_auth

logger = logging.getLogger(__name__)


@dataclass
class Thread:
    """Represents a Louie conversation thread."""

    id: str
    name: str | None = None
    folder: str | None = None


class Response:
    """Response containing output elements and optional streaming metadata."""

    def __init__(
        self,
        thread_id: str,
        elements: list[dict[str, Any]],
        *,
        stream_messages: list[dict[str, Any]] | None = None,
        include_reasoning: bool | None = None,
    ):
        """Initialize a response.

        Args:
            thread_id: The thread ID this response belongs to.
            elements: Latest output element snapshots in server position order.
            stream_messages: Ordered raw streaming envelopes when available.
            include_reasoning: Whether structural reasoning was requested. ``None``
                preserves conservative behavior for manually constructed responses.
        """
        self.thread_id = thread_id
        self.elements = elements
        self.stream_messages = list(stream_messages or [])
        self.include_reasoning = include_reasoning

    @staticmethod
    def _element_text(element: dict[str, Any]) -> str:
        """Extract text across current and legacy element field names."""
        content = (
            element.get("content")
            or element.get("text", "")
            or element.get("value", "")
        )
        return str(content) if content is not None else ""

    @property
    def text_elements(self) -> list[dict[str, Any]]:
        """Get all text elements, including opt-in reasoning elements."""
        return [e for e in self.elements if e.get("type") in ["TextElement", "text"]]

    @property
    def dataframe_elements(self) -> list[dict[str, Any]]:
        """Get all dataframe elements from the response."""
        return [e for e in self.elements if e.get("type") in ["DfElement", "df"]]

    @property
    def graph_elements(self) -> list[dict[str, Any]]:
        """Get all graph elements from the response."""
        return [e for e in self.elements if e.get("type") in ["GraphElement", "graph"]]

    @property
    def errors(self) -> list[dict[str, Any]]:
        """Get structured output error elements."""
        return [
            e
            for e in self.elements
            if e.get("type") in ["ExceptionElement", "exception", "error"]
        ]

    @property
    def has_dataframes(self) -> bool:
        """Check if response contains any dataframe elements."""
        return len(self.dataframe_elements) > 0

    @property
    def has_graphs(self) -> bool:
        """Check if response contains any graph elements."""
        return len(self.graph_elements) > 0

    @property
    def has_errors(self) -> bool:
        """Check for output errors or a failed streaming terminal."""
        return bool(self.errors) or self.succeeded is False

    @property
    def run_updates(self) -> list[dict[str, Any]]:
        """Ordered root and method run snapshots from the stream."""
        return [
            node
            for message in self.stream_messages
            if message.get("type") == "StreamingApiMessageRunUpdate"
            and isinstance((node := message.get("run_node")), dict)
        ]

    @property
    def phase_updates(self) -> list[dict[str, Any]]:
        """Ordered method-run snapshots, which represent execution phases."""
        return [
            node for node in self.run_updates if node.get("node_type") == "MethodRun"
        ]

    @property
    def run_nodes(self) -> list[dict[str, Any]]:
        """Latest snapshot for each run node, preserving first-seen order."""
        latest: dict[str, dict[str, Any]] = {}
        for node in self.run_updates:
            node_id = node.get("id")
            if node_id is not None:
                latest[str(node_id)] = node
        return list(latest.values())

    @property
    def phases(self) -> list[dict[str, Any]]:
        """Latest snapshot for each method-run execution phase."""
        return [node for node in self.run_nodes if node.get("node_type") == "MethodRun"]

    @property
    def root_run(self) -> dict[str, Any] | None:
        """Latest root-run snapshot, if the server emitted one."""
        for node in reversed(self.run_updates):
            if node.get("node_type") == "Run":
                return node
        return None

    @property
    def token_flow(self) -> dict[str, Any] | None:
        """Latest root-run token-flow counters, if available."""
        root = self.root_run
        value = root.get("token_flow") if root else None
        return value if isinstance(value, dict) else None

    @property
    def trace_events(self) -> list[Any]:
        """Returned server trace payloads (distinct from reasoning and traceparent)."""
        return [
            message.get("payload")
            for message in self.stream_messages
            if message.get("type") == "StreamingApiMessageTrace"
        ]

    @property
    def terminals(self) -> list[dict[str, Any]]:
        """All terminal envelopes; uploads may emit more than one."""
        return [
            message
            for message in self.stream_messages
            if message.get("type") == "StreamingApiMessageTerminal"
        ]

    @property
    def terminal(self) -> dict[str, Any] | None:
        """Last terminal envelope, representing whole-stream plumbing outcome."""
        terminals = self.terminals
        return terminals[-1] if terminals else None

    @property
    def terminal_error(self) -> str | None:
        """Error from the final terminal envelope, if any."""
        terminal = self.terminal
        error = terminal.get("error") if terminal else None
        return str(error) if error else None

    @property
    def succeeded(self) -> bool | None:
        """Final terminal success flag, independent of the agent run state."""
        terminal = self.terminal
        success = terminal.get("success") if terminal else None
        return success if isinstance(success, bool) else None

    @property
    def status(self) -> str:
        """Normalized execution status from terminal metadata and root-run state."""
        if self.succeeded is False:
            return "failed"

        root = self.root_run
        state = str(root.get("state", "")) if root else ""
        normalized = {
            "Scheduled": "scheduled",
            "Running": "running",
            "Done": "succeeded",
            "Failed": "failed",
            "Cancelled": "cancelled",
            "Interrupted": "interrupted",
        }.get(state)
        if normalized:
            return normalized
        if self.succeeded is True:
            return "succeeded"
        return "unknown"

    @property
    def final_answer_id(self) -> str | None:
        """Server-selected final-answer element ID, if available."""
        root = self.root_run
        value = root.get("final_answer") if root else None
        return str(value) if value else None

    def _is_reasoning_element(self, element: dict[str, Any]) -> bool:
        """Classify reasoning conservatively using old or current wire semantics."""
        if element.get("draft") is True:
            return True
        if self.include_reasoning is not True:
            return False

        root = self.root_run
        final_id = self.final_answer_id
        root_id = root.get("id") if root else None
        if not final_id or not root_id:
            return False
        return (
            element.get("type") in ["TextElement", "text"]
            and element.get("during_run_id") == root_id
            and str(element.get("id", "")) != final_id
        )

    @property
    def reasoning_elements(self) -> list[dict[str, Any]]:
        """Latest text snapshots classified as opt-in reasoning."""
        return [e for e in self.text_elements if self._is_reasoning_element(e)]

    @property
    def reasoning_texts(self) -> list[str]:
        """Text for each reasoning element in output order."""
        return [self._element_text(e) for e in self.reasoning_elements]

    @property
    def reasoning_text(self) -> str | None:
        """Reasoning parts joined for convenient reading."""
        parts = [part for part in self.reasoning_texts if part]
        return "\n\n".join(parts) if parts else None

    @property
    def final_text_elements(self) -> list[dict[str, Any]]:
        """Text outputs excluding elements classified as reasoning."""
        return [e for e in self.text_elements if not self._is_reasoning_element(e)]

    @property
    def final_texts(self) -> list[str]:
        """Non-reasoning text outputs in output order."""
        return [self._element_text(e) for e in self.final_text_elements]

    @property
    def final_text_element(self) -> dict[str, Any] | None:
        """Explicit final-answer element, or latest legacy non-reasoning text."""
        final_id = self.final_answer_id
        if final_id:
            for element in self.final_text_elements:
                if str(element.get("id", "")) == final_id:
                    return element
        elements = self.final_text_elements
        return elements[-1] if elements else None

    @property
    def final_text(self) -> str | None:
        """Explicit final answer, with latest-text fallback for legacy responses."""
        element = self.final_text_element
        return self._element_text(element) if element is not None else None

    @property
    def text(self) -> str | None:
        """Get the primary final-oriented text response.

        An explicit server final-answer pointer wins. Without one, preserve the
        historical SDK behavior of returning the first text element, excluding
        only an old wire-format element explicitly marked ``draft=true``.
        """
        final_id = self.final_answer_id
        if final_id and self.include_reasoning is True:
            element = self.final_text_element
            return self._element_text(element) if element is not None else None
        elements = self.final_text_elements
        return self._element_text(elements[0]) if elements else None

    @property
    def df(self) -> Any | None:
        """Get the first DataFrame from the response."""
        df_elems = self.dataframe_elements
        if not df_elems:
            return None
        first_df = df_elems[0]
        return first_df.get("table")

    @property
    def dfs(self) -> list[Any]:
        """Get all DataFrames from the response."""
        return [elem["table"] for elem in self.dataframe_elements if "table" in elem]


class LouieClient:
    """
    Enhanced client for Louie.ai that matches the documented API.

    This client provides thread-based conversations with natural language queries.

    Authentication can be handled in multiple ways:
    1. Pass an existing Graphistry client
    2. Pass credentials directly
    3. Use existing graphistry.register() authentication
    4. Provide a bearer token (Graphistry or anonymous)
    """

    def __init__(
        self,
        server_url: str = "https://den.louie.ai",
        graphistry_client: Any | None = None,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        personal_key_id: str | None = None,
        personal_key_secret: str | None = None,
        org_name: str | None = None,
        api: int = 3,
        server: str | None = None,
        anonymous: bool = False,
        anonymous_token: str | None = None,
        anonymous_timeout: float = 20.0,
        timeout: float = 300.0,  # 5 minutes default for agentic flows
        streaming_timeout: float = 120.0,  # 2 minutes for streaming chunks
        token: str | None = None,
        graphistry_server: str | None = None,
    ):
        """Initialize the Louie client.

        Args:
            server_url: Base URL for the Louie.ai service (default: den)
            graphistry_client: Existing Graphistry client to use for auth
            username: Username for direct authentication
            password: Password for direct authentication
            api_key: API key for direct authentication (legacy)
            personal_key_id: Personal key ID for service account authentication
            personal_key_secret: Personal key secret for service account authentication
            org_name: Organization name - use username for personal orgs (optional)
            api: API version (default: 3)
            anonymous: Use anonymous auth via /auth/anonymous (local desktop only)
            anonymous_timeout: Timeout for /auth/anonymous in seconds
            timeout: Overall timeout in seconds for requests (default: 300s/5min)
            streaming_timeout: Timeout for streaming chunks (default: 120s/2min)
            token: Optional pre-fetched bearer token (anonymous or Graphistry)
            graphistry_server: Graphistry server URL for direct authentication

        Examples:
            # Use existing graphistry authentication
            client = LouieClient()

            # Pass username/password credentials
            client = LouieClient(
                username="user",
                password="pass",
                graphistry_server="hub.graphistry.com"
            )

            # Use personal key authentication (recommended for service accounts)
            client = LouieClient(
                personal_key_id="<your-personal-key-id>",
                personal_key_secret="<your-personal-key-secret>",
                graphistry_server="hub.graphistry.com"
            )

            # Specify organization
            client = LouieClient(
                username="user",
                password="pass",
                org_name="my-org",
                graphistry_server="hub.graphistry.com"
            )

            # Use existing graphistry client
            g = graphistry.nodes(df)
            client = LouieClient(graphistry_client=g)

            # Anonymous auth for local desktop (if enabled)
            client = LouieClient(
                server_url="http://localhost:8513",
                anonymous=True
            )

            # Direct bearer token (no refresh)
            client = LouieClient(
                server_url="https://den.louie.ai",
                token="<token>"
            )
        """
        self.server_url = server_url.rstrip("/")
        self._timeout = timeout
        self._streaming_timeout = streaming_timeout
        self._client = httpx.Client(timeout=timeout)

        if server is not None:
            raise ValueError(
                "server is no longer supported; use graphistry_server instead."
            )
        if anonymous_token is not None:
            raise ValueError(
                "anonymous_token is no longer supported; "
                "use token (with anonymous=True) instead."
            )

        if anonymous and any(
            [
                graphistry_client is not None,
                username,
                password,
                api_key,
                personal_key_id,
                personal_key_secret,
                graphistry_server,
            ]
        ):
            raise ValueError(
                "Anonymous auth cannot be combined with Graphistry credentials."
            )
        if (
            token is not None
            and not anonymous
            and any(
                [
                    graphistry_client is not None,
                    username,
                    password,
                    api_key,
                    personal_key_id,
                    personal_key_secret,
                    graphistry_server,
                ]
            )
        ):
            raise ValueError(
                "Token auth cannot be combined with Graphistry credentials."
            )

        # Set up authentication
        self._auth_manager = AuthManager(
            graphistry_client=graphistry_client,
            username=username,
            password=password,
            api_key=api_key,
            personal_key_id=personal_key_id,
            personal_key_secret=personal_key_secret,
            org_name=org_name,
            api=api,
            graphistry_server=graphistry_server,
            token=token,
            anonymous=anonymous,
            anonymous_timeout=anonymous_timeout,
            anonymous_server_url=self.server_url,
        )

        # If credentials provided, authenticate immediately
        if any([username, password, api_key, personal_key_id, personal_key_secret]):
            # Build kwargs for register, excluding None values
            register_kwargs: dict[str, Any] = {}
            if personal_key_id is not None and personal_key_secret is not None:
                # Use personal key authentication
                register_kwargs["personal_key_id"] = personal_key_id
                register_kwargs["personal_key_secret"] = personal_key_secret
            elif api_key is not None:
                # Use API key authentication
                register_kwargs["key"] = api_key  # graphistry uses 'key' parameter
            elif username is not None and password is not None:
                # Use username/password authentication
                register_kwargs["username"] = username
                register_kwargs["password"] = password

            # Add common parameters
            if org_name is not None:
                register_kwargs["org_name"] = org_name
            if api is not None:
                register_kwargs["api"] = api
            if graphistry_server is not None:
                register_kwargs["server"] = graphistry_server

            if register_kwargs:
                self.register(**register_kwargs)

    @property
    def auth_manager(self) -> AuthManager:
        """Get the authentication manager."""
        return self._auth_manager

    def register(self, **kwargs: Any) -> LouieClient:
        """Register authentication credentials (passthrough to graphistry).

        Args:
            **kwargs: Same arguments as graphistry.register()

        Returns:
            Self for chaining

        Examples:
            client.register(username="user", password="pass")
            client.register(api_key="key-123")
        """
        self._auth_manager.register(**kwargs)
        return self

    @auto_retry_auth
    def _fetch_dataframe_arrow(
        self, thread_id: str, block_id: str
    ) -> pd.DataFrame | None:
        """Fetch a dataframe using Arrow format.

        Args:
            thread_id: The thread ID
            block_id: The block ID for the dataframe

        Returns:
            DataFrame or None if fetch fails
        """
        try:
            headers = self._get_headers()
            url = f"{self.server_url}/api/dthread/{thread_id}/df/block/{block_id}/arrow"

            response = self._client.get(url, headers=headers)
            response.raise_for_status()

            # Parse Arrow format
            # Try file format first (most common), then stream format
            try:
                file_reader = pa.ipc.open_file(response.content)
                table = file_reader.read_all()
            except Exception:
                # Fallback to stream format
                stream_reader = pa.ipc.open_stream(response.content)
                table = stream_reader.read_all()

            # Convert to pandas
            df = table.to_pandas()
            return df

        except Exception as e:
            import warnings

            warnings.warn(
                f"Failed to fetch dataframe {block_id} from thread {thread_id}. "
                f"URL: {url if 'url' in locals() else 'not constructed'}. "
                f"Error: {type(e).__name__}: {e}",
                RuntimeWarning,
                stacklevel=2,
            )
            logger.debug("Full error details: ", exc_info=True)
            return None

    def _get_headers(
        self, session_trace_id: str | None = None, traceparent: str | None = None
    ) -> dict[str, str]:
        """Get authorization headers using auth manager.

        Args:
            session_trace_id: Optional session trace ID for correlation when
                OTel is not available. Used to generate traceparent if no
                explicit traceparent is provided and OTel is not active.
            traceparent: Optional explicit traceparent header value. If provided,
                takes precedence over auto-generated values.

        Returns:
            Headers dict with Authorization and optionally traceparent.
        """
        token = self._auth_manager.get_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Add organization header if available
        if hasattr(
            self._auth_manager, "_credentials"
        ) and self._auth_manager._credentials.get("org_name"):
            org_name = self._auth_manager._credentials["org_name"]
            # Convert to slug format (lowercase, replace special chars with hyphens)
            if org_name:  # Ensure org_name is not None
                org_slug = self._to_slug(str(org_name))
                headers["X-Graphistry-Org"] = org_slug

        # Add traceparent for distributed tracing
        # Priority: explicit traceparent > OTel context > session trace
        if traceparent:
            headers["traceparent"] = traceparent
        else:
            tp = get_traceparent(session_trace_id)
            if tp:
                headers["traceparent"] = tp

        return headers

    def _to_slug(self, text: str) -> str:
        """Convert text to slug format.

        - Lowercase
        - Replace spaces and special chars with hyphens
        - Remove consecutive hyphens
        - Strip leading/trailing hyphens
        """
        import re

        # Convert to lowercase
        slug = text.lower()
        # Replace any non-alphanumeric character with hyphen
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        # Remove consecutive hyphens
        slug = re.sub(r"-+", "-", slug)
        # Strip leading/trailing hyphens
        slug = slug.strip("-")
        return slug

    @staticmethod
    def _decode_json_objects(response_text: str) -> list[dict[str, Any]]:
        """Decode newline-delimited or concatenated top-level JSON objects."""
        objects: list[dict[str, Any]] = []
        decoder = json.JSONDecoder()
        for line in response_text.splitlines():
            index = 0
            while index < len(line):
                while index < len(line) and line[index].isspace():
                    index += 1
                if index >= len(line):
                    break
                try:
                    value, end_index = decoder.raw_decode(line, index)
                except json.JSONDecodeError:
                    break
                if isinstance(value, dict):
                    objects.append(value)
                index = end_index
        return objects

    @classmethod
    def _parse_stream_objects(cls, objects: list[Any]) -> dict[str, Any]:
        """Accumulate typed or legacy stream objects into a lossless response."""
        result: dict[str, Any] = {
            "dthread_id": None,
            "elements": [],
            "stream_messages": [],
        }
        elements_by_key: dict[str, dict[str, Any]] = {}
        element_positions: dict[str, int] = {}
        element_orders: dict[str, int] = {}
        position_keys: dict[int, str] = {}

        for sequence, data in enumerate(objects):
            if not isinstance(data, dict):
                continue
            result["stream_messages"].append(data)

            if "dthread_id" in data:
                result["dthread_id"] = data["dthread_id"]

            msg_type = data.get("type")
            elem: dict[str, Any] | None = None
            if msg_type == "StreamingApiMessageOutputUpdate":
                payload = data.get("payload")
                if isinstance(payload, dict):
                    elem = payload
            elif msg_type is None and isinstance(data.get("payload"), dict):
                elem = data["payload"]

            if elem is None:
                continue

            position = data.get("position")
            elem_id = elem.get("id")
            if elem_id:
                key = f"id:{elem_id}"
            elif isinstance(position, int):
                key = f"position:{position}"
            else:
                key = f"message:{sequence}"

            if isinstance(position, int):
                previous_key = position_keys.get(position)
                if previous_key is not None and previous_key != key:
                    elements_by_key.pop(previous_key, None)
                    element_positions.pop(previous_key, None)
                    element_orders.pop(previous_key, None)
                position_keys[position] = key
                element_positions[key] = position

            element_orders.setdefault(key, sequence)
            cls._merge_element(elem, elements_by_key, key=key)

        keys = sorted(
            elements_by_key,
            key=lambda key: (
                0,
                element_positions[key],
            )
            if key in element_positions
            else (1, element_orders[key]),
        )
        result["elements"] = [elements_by_key[key] for key in keys]
        return result

    def _parse_jsonl_response(self, response_text: str) -> dict[str, Any]:
        """Parse typed NDJSON, legacy JSONL, or concatenated JSON objects."""
        return self._parse_stream_objects(self._decode_json_objects(response_text))

    @staticmethod
    def _merge_element(
        elem: dict[str, Any],
        elements_by_id: dict[str, dict[str, Any]],
        *,
        key: str | None = None,
    ) -> None:
        """Merge a full or partial element snapshot, including empty updates."""
        resolved_key = key or (
            f"id:{elem['id']}" if elem.get("id") else f"anonymous:{len(elements_by_id)}"
        )
        existing = elements_by_id.get(resolved_key)
        if existing is None:
            elements_by_id[resolved_key] = dict(elem)
        else:
            existing.update(elem)

    def _attach_dataframes(
        self, thread_id: str, elements: list[dict[str, Any]]
    ) -> None:
        """Fetch and attach dataframe contents for DataFrame elements."""

        if not thread_id:
            return

        for elem in elements:
            if elem.get("type") in ["DfElement", "df", "DataFrame", "dataframe"]:
                # Workaround: server GCs empty DFs before fetch (#40)
                shape = (elem.get("metadata") or {}).get("shape", [])
                if shape and shape[0] == 0:
                    elem["table"] = pd.DataFrame()
                    continue

                df_id = (
                    elem.get("df_id")
                    or elem.get("block_id")
                    or (elem.get("data") or {}).get("df_id")
                    or (elem.get("data") or {}).get("block_id")
                    or elem.get("id")
                )
                if not df_id:
                    continue
                fetched = self._fetch_dataframe_arrow(thread_id, df_id)
                if fetched is not None:
                    elem["table"] = fetched
                else:
                    logger.warning(
                        f"Failed to fetch dataframe {df_id} from thread "
                        f"{thread_id} for DfElement. Element: {elem}"
                    )

    def _chat_singleshot(
        self, params: dict[str, Any], *, include_reasoning: bool = False
    ) -> Response:
        """Call the batch chat endpoint and return a metadata-preserving Response."""

        headers = self._get_headers()
        response = self._client.post(
            f"{self.server_url}/api/chat_singleshot/",
            headers=headers,
            params=params,
            timeout=self._timeout,
        )
        response.raise_for_status()

        payload = response.json()
        objects = payload if isinstance(payload, list) else [payload]
        parsed = self._parse_stream_objects(objects)
        dthread_id = parsed.get("dthread_id") or ""
        elements = parsed.get("elements", [])
        self._attach_dataframes(dthread_id, elements)
        return Response(
            thread_id=dthread_id,
            elements=elements,
            stream_messages=parsed.get("stream_messages", []),
            include_reasoning=include_reasoning,
        )

    def create_thread(
        self,
        name: str | None = None,
        folder: str | None = None,
        initial_prompt: str | None = None,
        *,
        agent: str = "LouieAgent",
        traces: bool = False,
        include_reasoning: bool = False,
        share_mode: ShareMode = "Private",
        table_ai_overrides: TableAIOverrides | Mapping[str, Any] | None = None,
        **override_kwargs: Any,
    ) -> Thread:
        """Create a new conversation thread.

        Args:
            name: Optional name for the thread
            folder: Optional folder path for the thread (server support required)
            initial_prompt: Optional first message to initialize thread
            agent: Agent to use for initial prompt (default: LouieAgent)
            traces: Whether to request server trace events (default: False)
            include_reasoning: Whether to include the agent's provisional reasoning text
                (default: False).
            share_mode: Visibility mode for initial message
            table_ai_overrides: Structured Table AI overrides applied to initial prompt
            **override_kwargs: Legacy Table AI override keyword arguments forwarded to
                `add_cell` (e.g., `table_ai_semantic_mode`). Prefer
                `table_ai_overrides`.

        Returns:
            Thread object with ID

        Note: If no initial_prompt, thread ID will be empty until first add_cell
        """
        if initial_prompt:
            # Create thread with initial message
            add_kwargs = dict(override_kwargs)
            if table_ai_overrides is not None:
                add_kwargs["table_ai_overrides"] = table_ai_overrides

            response = self.add_cell(
                "",
                initial_prompt,
                agent=agent,
                name=name,
                folder=folder,
                traces=traces,
                include_reasoning=include_reasoning,
                share_mode=share_mode,
                **add_kwargs,
            )
            return Thread(id=response.thread_id, name=name, folder=folder)
        else:
            # Return placeholder - actual thread created on first add_cell
            return Thread(id="", name=name, folder=folder)

    @auto_retry_auth
    def add_cell(
        self,
        thread_id: str,
        prompt: str,
        agent: str = "LouieAgent",
        *,
        name: str | None = None,
        folder: str | None = None,
        traces: bool = False,
        include_reasoning: bool = False,
        share_mode: ShareMode = "Private",
        user_agent: UserAgent = "API",
        table_ai_overrides: TableAIOverrides | Mapping[str, Any] | None = None,
        use_batch: bool | None = None,
        session_trace_id: str | None = None,
        **legacy_overrides: Any,
    ) -> Response:
        """Add a cell (query) to a thread and get response.

        Args:
            thread_id: Thread ID to add to (empty string creates new thread)
            prompt: Natural language query
            agent: Agent to use (default: LouieAgent)
            name: Optional thread name (applied only when creating a new thread)
            folder: Optional folder path (applied only when creating a new thread)
            traces: Whether to request server trace events (default: False)
            include_reasoning: Include the agent's provisional reasoning
                text in addition to final response elements (default: False).
            share_mode: Visibility mode - "Private", "Organization", or "Public"
            user_agent: DataThread creation_user_agent — "API" or "Louie"
            table_ai_overrides: Structured overrides via dataclass or mapping.
            use_batch: Force singleshot (`True`) or streaming (`False`); defaults to
                singleshot when overrides are provided.
            session_trace_id: Optional session trace ID for distributed tracing
                correlation when OpenTelemetry is not available.
            **legacy_overrides: Backwards-compatible Table AI keyword arguments like
                ``table_ai_semantic_mode``. Prefer `table_ai_overrides`.

        Returns:
            Response object containing thread_id and all elements
        """
        headers = self._get_headers(session_trace_id=session_trace_id)

        # Build query parameters
        params: dict[str, Any] = {
            "query": prompt,
            "agent": agent,
            # Convert bool to string for HTTP params
            "ignore_traces": str(not traces).lower(),
            "include_reasoning": str(include_reasoning).lower(),
            "share_mode": share_mode,
            "user_agent": user_agent,
        }

        # Add thread ID if continuing existing thread
        if thread_id:
            params["dthread_id"] = thread_id
        else:
            if name:
                params["name"] = name
            if folder:
                params["folder"] = folder

        overrides: dict[str, Any] = normalize_table_ai_overrides(table_ai_overrides)
        legacy_params = collect_table_ai_kwargs(legacy_overrides)
        if legacy_overrides:
            unexpected = ", ".join(sorted(legacy_overrides))
            raise TypeError(
                f"add_cell() got unexpected keyword argument(s): {unexpected}"
            )
        overrides.update(legacy_params)
        params.update(overrides)

        if use_batch or (use_batch is None and bool(overrides)):
            return self._chat_singleshot(params, include_reasoning=include_reasoning)

        # Make streaming request with custom timeout handling
        response_text = ""
        lines_received = 0
        start_time = time.time()

        # Use configured timeouts
        stream_client = httpx.Client(
            timeout=httpx.Timeout(
                self._timeout,  # Overall timeout
                read=self._streaming_timeout,  # Per-chunk timeout
            )
        )

        with stream_client:
            with stream_client.stream(
                "POST", f"{self.server_url}/api/chat/", headers=headers, params=params
            ) as response:
                response.raise_for_status()

                # Collect streaming lines
                last_activity = start_time
                try:
                    for line in response.iter_lines():
                        if line:
                            response_text += line + "\n"
                            lines_received += 1
                            last_activity = time.time()

                            # Keep reading all elements until stream ends
                            # Don't break early just because we got a text element

                        # Only timeout if no activity for streaming_timeout duration
                        # Allow total_timeout for overall request
                        # but don't break active streams
                        time_since_activity = time.time() - last_activity
                        if time_since_activity > self._streaming_timeout:
                            logger.warning(
                                f"Streaming timeout after {time_since_activity:.1f}s "
                                f"of inactivity. "
                                f"Received {lines_received} lines. "
                                f"This may result in truncated responses."
                            )
                            break

                except httpx.ReadTimeout as e:
                    elapsed = time.time() - start_time
                    # Accept any response with at least the thread ID line
                    # Don't require minimum line count that could drop
                    # valid short responses
                    if lines_received >= 1:
                        logger.debug(
                            f"ReadTimeout after {elapsed:.1f}s with "
                            f"{lines_received} lines received. "
                            f"Treating as complete response."
                        )
                    else:
                        raise RuntimeError(
                            f"Louie API timeout after {elapsed:.1f}s waiting for "
                            f"response. Only received {lines_received} lines. "
                            f"Agentic flows can take time - consider increasing "
                            f"timeout (current: {self._streaming_timeout}s per chunk, "
                            f"{self._timeout}s total). "
                            f"Set timeout parameter when creating LouieClient."
                        ) from e

        # Log if request took a long time
        total_time = time.time() - start_time
        if total_time > 30:
            import warnings

            warnings.warn(
                f"Louie API request took {total_time:.1f}s to complete. "
                f"This is normal for complex agentic flows, but if you're "
                f"seeing timeouts, consider increasing the timeout parameter "
                f"when creating LouieClient.",
                RuntimeWarning,
                stacklevel=2,
            )

        # Parse JSONL response
        result = self._parse_jsonl_response(response_text)

        # Get the thread ID
        actual_thread_id = result.get("dthread_id") or thread_id

        elements = result.get("elements", [])
        self._attach_dataframes(actual_thread_id, elements)

        # Return Response with all elements
        return Response(
            thread_id=actual_thread_id,
            elements=elements,
            stream_messages=result.get("stream_messages", []),
            include_reasoning=include_reasoning,
        )

    def __call__(
        self,
        prompt: str,
        *,
        thread_id: str | None = None,
        traces: bool = False,
        agent: str = "LouieAgent",
        share_mode: ShareMode = "Private",
        **kwargs: Any,
    ) -> Response:
        """Make the client callable for ergonomic usage.

        This allows using the client like a function:
        ```python
        client = LouieClient()
        response = client("What's the weather?")
        ```

        Args:
            prompt: Natural language query
            thread_id: Thread ID to use (None creates new thread)
            traces: Whether to request server trace events
            agent: Agent to use (default: LouieAgent)
            share_mode: Visibility mode - "Private", "Organization", or "Public"
            **kwargs: Additional keyword arguments forwarded to `add_cell`

        Returns:
            Response object containing thread_id and all elements
        """
        # Use empty string for new thread if thread_id is None
        tid = thread_id if thread_id is not None else ""

        # Store the thread_id for subsequent calls if not provided
        if not hasattr(self, "_current_thread_id"):
            self._current_thread_id = None

        # Use stored thread_id if none provided
        if thread_id is None and self._current_thread_id is not None:
            tid = self._current_thread_id

        # Make the call
        response = self.add_cell(
            thread_id=tid,
            prompt=prompt,
            agent=agent,
            traces=traces,
            share_mode=share_mode,
            **kwargs,
        )

        # Store thread_id for next call
        if response.thread_id:
            self._current_thread_id = response.thread_id

        return response

    @auto_retry_auth
    def list_threads(
        self, page: int = 1, page_size: int = 20, *, folder: str | None = None
    ) -> list[Thread]:
        """List available threads.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            folder: Optional folder path to filter results (client-side)

        Returns:
            List of Thread objects
        """
        headers = self._get_headers()

        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
            "sort_by": "last_modified",
            "sort_order": "desc",
        }
        if folder:
            params["folder"] = folder

        response = self._client.get(
            f"{self.server_url}/api/dthreads",
            headers=headers,
            params=params,
        )
        response.raise_for_status()

        data = response.json()
        items = data.get("data") or data.get("items") or []
        if not isinstance(items, list):
            items = []

        if folder is not None:
            items = [
                item
                for item in items
                if isinstance(item, dict) and item.get("folder") == folder
            ]

        threads = []
        for item in items:
            if not isinstance(item, dict):
                continue
            threads.append(
                Thread(
                    id=item.get("id", ""),
                    name=item.get("name"),
                    folder=item.get("folder"),
                )
            )

        return threads

    @auto_retry_auth
    def get_thread(self, thread_id: str) -> Thread:
        """Get a specific thread by ID.

        Args:
            thread_id: Thread ID to retrieve

        Returns:
            Thread object
        """
        data = self._fetch_thread_manifest(thread_id)
        return Thread(
            id=data.get("id", ""),
            name=data.get("name"),
            folder=data.get("folder"),
        )

    @auto_retry_auth
    def get_thread_by_name(self, name: str) -> Thread:
        """Get a thread by name (server resolves exact/fuzzy matches).

        Args:
            name: Thread name to retrieve

        Returns:
            Thread object
        """
        data = self._fetch_thread_manifest(name)
        return Thread(
            id=data.get("id", ""),
            name=data.get("name"),
            folder=data.get("folder"),
        )

    def _fetch_thread_manifest(self, identifier: str) -> dict[str, Any]:
        headers = self._get_headers()
        response = self._client.get(
            f"{self.server_url}/api/dthread/{identifier}", headers=headers
        )
        if response.status_code == 404:
            response = self._client.get(
                f"{self.server_url}/api/dthreads/{identifier}", headers=headers
            )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Thread manifest response was not an object.")
        return cast(dict[str, Any], data)

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
        session_trace_id: str | None = None,
    ) -> Response:
        """Upload a DataFrame with a natural language query for AI analysis.

        Args:
            prompt: Natural language query about the data
            df: Pandas DataFrame to analyze
            thread_id: Thread ID to continue conversation
            format: Serialization format (parquet, csv, json, jsonl, arrow)
            agent: AI agent to use
            traces: Request server trace events
            share_mode: Visibility setting
            name: Optional thread name
            folder: Optional folder path for the thread (server support required)
            parsing_options: Format-specific parsing options
            session_trace_id: Optional session trace ID for distributed tracing
                correlation when OpenTelemetry is not available.

        Returns:
            Response object with analysis results
        """
        # Lazy import to avoid circular dependency
        from ._upload import UploadClient

        if not hasattr(self, "_upload_client"):
            self._upload_client = UploadClient(self)

        return self._upload_client.upload_dataframe(
            prompt=prompt,
            df=df,
            thread_id=thread_id,
            format=format,
            agent=agent,
            traces=traces,
            include_reasoning=include_reasoning,
            share_mode=share_mode,
            name=name,
            folder=folder,
            parsing_options=parsing_options,
            session_trace_id=session_trace_id,
        )

    def upload_image(
        self,
        prompt: str,
        image: Any,
        thread_id: str = "",
        *,
        agent: str = "UploadPassthroughAgent",
        traces: bool = False,
        include_reasoning: bool = False,
        share_mode: str = "Private",
        name: str | None = None,
        folder: str | None = None,
        session_trace_id: str | None = None,
    ) -> Response:
        """Upload an image with a natural language query for analysis.

        Args:
            prompt: Natural language query about the image
            image: Image to analyze (file path, bytes, file-like, or PIL Image)
            thread_id: Thread ID to continue conversation
            agent: AI agent to use
            traces: Request server trace events
            share_mode: Visibility setting
            name: Optional thread name
            folder: Optional folder path for the thread (server support required)
            session_trace_id: Optional session trace ID for distributed tracing
                correlation when OpenTelemetry is not available.

        Returns:
            Response object with analysis results
        """
        from ._upload import UploadClient

        if not hasattr(self, "_upload_client"):
            self._upload_client = UploadClient(self)

        return self._upload_client.upload_image(
            prompt=prompt,
            image=image,
            thread_id=thread_id,
            agent=agent,
            traces=traces,
            include_reasoning=include_reasoning,
            share_mode=share_mode,
            name=name,
            folder=folder,
            session_trace_id=session_trace_id,
        )

    def upload_binary(
        self,
        prompt: str,
        file: Any,
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

        Args:
            prompt: Natural language query about the file
            file: File to analyze (file path, bytes, or file-like)
            thread_id: Thread ID to continue conversation
            agent: AI agent to use
            traces: Request server trace events
            share_mode: Visibility setting
            name: Optional thread name
            folder: Optional folder path for the thread (server support required)
            filename: Optional filename to use
            session_trace_id: Optional session trace ID for distributed tracing
                correlation when OpenTelemetry is not available.

        Returns:
            Response object with analysis results
        """
        from ._upload import UploadClient

        if not hasattr(self, "_upload_client"):
            self._upload_client = UploadClient(self)

        return self._upload_client.upload_binary(
            prompt=prompt,
            file=file,
            thread_id=thread_id,
            agent=agent,
            traces=traces,
            include_reasoning=include_reasoning,
            share_mode=share_mode,
            name=name,
            folder=folder,
            filename=filename,
            session_trace_id=session_trace_id,
        )

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up client on exit."""
        self._client.close()
