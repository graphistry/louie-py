"""Agent names a Louie server accepts as ``agent=`` and can run.

Single source of truth for the docs lint in ``test_docs_agent_names.py``.
Mirrors the Louie server: names in its ``AgentType`` that are registered as
runnable agents (``register_agent``), minus internal-only ones. Update this
file when the server adds, renames, or removes an agent; the lint then flags
every doc, notebook, README example, or docstring that needs to follow.
"""

# Available on every Louie deployment (Louie Web, self-hosted, Louie Desktop).
AGENTS = {
    "LouieAgent",  # default; routes to tools such as web search
    "TextAgent",
    "DoNothingAgent",
    "CodeAgent",
    "CodePassthroughAgent",
    "DatabricksAgent",
    "DatabricksPassthroughAgent",
    "GraphAgent",
    "GraphPassthroughAgent",
    "GraphUMAPPassthroughAgent",
    "KeplerAgent",  # when the server configures a map tile source
    "Kusto",
    "KustoPassthrough",
    "MCPAgent",
    "MermaidAgent",
    "MermaidPassthroughAgent",
    "NotebookTool",
    "OpenSearchAgent",
    "OpenSearchPassthroughAgent",
    "PerspectiveAgent",
    "PerspectivePassthroughAgent",
    "Splunk",
    "SplunkPassthrough",
    "TimelineAgent",  # when the server enables timelines
    "UploadPassthroughAgent",
}

# Louie servers only (not Louie Desktop).
SERVER_ONLY_AGENTS = {
    "BigQueryAgent",
    "BigQueryPassthroughAgent",
    "CockroachDBAgent",
    "CockroachDBPassthroughAgent",
    "MSSQLAgent",
    "MSSQLPassthroughAgent",
    "MySQLAgent",
    "MySQLPassthroughAgent",
    "NeptuneAgent",
    "NeptunePassthroughAgent",
    "PostgresAgent",
    "PostgresPassthroughAgent",
    "SpannerAgent",
    "SpannerPassthroughAgent",
    "TableAIAgent",
}

RUNNABLE_AGENTS = AGENTS | SERVER_ONLY_AGENTS
