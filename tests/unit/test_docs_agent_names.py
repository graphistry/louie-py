"""Docs and examples may only pass agent names a Louie server can run (#52).

Names come from ``agent_catalog.py``; a typo, a renamed agent (e.g. the old
``SplunkAgent``), or a name the server accepts but never registers (e.g.
``SnowflakeAgent``) fails here instead of with a 400 or an empty answer.
"""

import json
import re
from pathlib import Path

import pytest

from .agent_catalog import RUNNABLE_AGENTS

REPO = Path(__file__).resolve().parents[2]

AGENT_ARG = re.compile(r"""agent\s*=\s*["']([A-Za-z]+)["']""")


def _sources():
    yield from sorted((REPO / "docs").rglob("*.md"))
    yield from sorted((REPO / "docs").rglob("*.ipynb"))
    yield REPO / "README.md"
    yield from sorted((REPO / "src" / "louieai").rglob("*.py"))


def _code(path: Path) -> str:
    """File text; for notebooks, cell sources only (not recorded outputs)."""
    text = path.read_text(encoding="utf-8")
    if path.suffix != ".ipynb":
        return text
    cells = json.loads(text).get("cells", [])
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in cells
        if cell.get("cell_type") in ("code", "markdown")
    )


@pytest.mark.parametrize(
    "path", list(_sources()), ids=lambda p: str(p.relative_to(REPO))
)
def test_only_runnable_agent_names_passed(path):
    unknown = sorted(set(AGENT_ARG.findall(_code(path))) - RUNNABLE_AGENTS)
    assert not unknown, (
        f"{path.relative_to(REPO)} passes agent names no Louie server runs: "
        f"{unknown} (see tests/unit/agent_catalog.py)"
    )
