"""Docs must not recommend agent names the server rejects (issue #52).

Current Louie servers answer these with ``400 Invalid agent '<name>'``. A page
may still mention one as the *old* name, but never pass it as ``agent=``.
"""

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

REMOVED_AGENTS = {
    "SplunkAgent": "Splunk",
    "SplunkPassthroughAgent": "SplunkPassthrough",
    "KustoAgent": "Kusto",
    "KustoPassthroughAgent": "KustoPassthrough",
    "NotebookAgent": "NotebookTool",
    "FirecrawlAgent": "(omit agent=; LouieAgent routes web search)",
    "UploadAgent": "UploadPassthroughAgent",
}

AGENT_ARG = re.compile(r"""agent\s*=\s*["']([A-Za-z]+)["']""")


def _sources():
    yield from sorted((REPO / "docs").rglob("*.md"))
    yield from sorted((REPO / "docs").rglob("*.ipynb"))
    yield REPO / "README.md"
    yield from sorted((REPO / "src" / "louieai").rglob("*.py"))


def _code(path: Path) -> str:
    """File text; for notebooks, only code cell sources (not recorded outputs)."""
    text = path.read_text(encoding="utf-8")
    if path.suffix != ".ipynb":
        return text
    cells = json.loads(text).get("cells", [])
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in cells
        if cell.get("cell_type") == "code"
    )


@pytest.mark.parametrize(
    "path", list(_sources()), ids=lambda p: str(p.relative_to(REPO))
)
def test_no_removed_agent_names_passed(path):
    text = _code(path)
    stale = {
        name: REMOVED_AGENTS[name]
        for name in AGENT_ARG.findall(text)
        if name in REMOVED_AGENTS
    }
    assert not stale, f"{path.relative_to(REPO)} passes removed agent names: {stale}"
