#!/usr/bin/env python3
"""Automated tests for documentation code examples.

This module ensures all code examples in our documentation remain valid.
Can be run in CI/CD pipelines with mocked responses.
"""

import json
import re
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# Import from same directory when running tests
try:
    from .mocks import (
        MockDataFrame,
        create_mock_client,
        create_mock_response,
    )
except ImportError:
    # Fall back to direct import when running from unit directory
    from mocks import (
        MockDataFrame,
        create_mock_client,
        create_mock_response,
    )


def extract_python_blocks(markdown_path: Path) -> list[tuple[str, int, str]]:
    """Extract Python code blocks from markdown file.

    Returns:
        List of (code, line_number, context) tuples
    """
    content = markdown_path.read_text()
    blocks = []

    # Match ```python code blocks
    pattern = r"```python\n(.*?)\n```"

    for match in re.finditer(pattern, content, re.DOTALL):
        code = match.group(1)
        line_num = content[: match.start()].count("\n") + 1

        # Get context - the heading or text before the code block
        lines_before = content[: match.start()].strip().split("\n")
        context = ""
        for line in reversed(lines_before):
            if line.strip():
                context = line.strip()
                break

        blocks.append((code, line_num, context))

    return blocks


def should_skip_code(code: str) -> bool:
    """Determine if code block should be skipped."""
    skip_patterns = [
        "$ ",  # Shell commands
        "pip install",
        "uv pip",
        "...",  # Incomplete code
        "# TODO",
    ]
    return any(pattern in code for pattern in skip_patterns)


def preprocess_code(code: str) -> str:
    """Preprocess code to handle common documentation patterns."""
    # Replace placeholder values
    replacements = {
        '"your_user"': '"test_user"',
        '"your_pass"': '"test_pass"',
        "'your_user'": "'test_user'",
        "'your_pass'": "'test_pass'",
        "hub.graphistry.com": "test.graphistry.com",
    }

    for old, new in replacements.items():
        code = code.replace(old, new)

    return code


def create_test_namespace(client):
    """Create namespace with all necessary mocks for code execution."""
    # Mock modules
    mock_graphistry = Mock()
    mock_graphistry.register = Mock()
    mock_graphistry.api_token = Mock(return_value="fake-token")
    mock_graphistry.nodes = Mock(return_value=mock_graphistry)
    mock_graphistry.edges = Mock(return_value=mock_graphistry)

    # Mock louieai module
    mock_louieai = Mock()
    mock_louieai.LouieClient = Mock(return_value=client)

    # Create some pre-existing objects that snippets might reference
    thread = client.create_thread(name="Test Thread")
    response = client.add_cell(thread.id, "test query")
    response1 = client.add_cell(thread.id, "query data")
    response2 = client.add_cell(thread.id, "analyze results")

    # File operations mock
    mock_file = Mock()
    mock_file.write = Mock(return_value=None)
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock()

    namespace = {
        "__builtins__": __builtins__,
        "print": lambda *args, **kwargs: None,  # Suppress output
        "open": Mock(return_value=mock_file),
        "client": client,
        "thread": thread,
        "response": response,
        "response1": response1,
        "response2": response2,
        "response3": create_mock_response("graph", thread.id),
        "response4": create_mock_response("text", thread.id),
        "df": MockDataFrame(),
        "df2": MockDataFrame(),
        "threads": [thread],
        "graphistry": mock_graphistry,
        "louieai": mock_louieai,  # Add louieai module
        "g": mock_graphistry,
        "pd": pd,  # Real pandas for type checks
        "json": json,
        "save_base64_image": Mock(),  # Mock function referenced in docs
    }

    return namespace


@pytest.mark.unit
class TestDocumentation:
    """Test all documentation code examples."""

    def _test_code_block(self, code: str, doc_file: str, line_num: int):
        """Test a single code block."""
        if should_skip_code(code):
            pytest.skip("Non-executable code")

        code = preprocess_code(code)
        client = create_mock_client()
        namespace = create_test_namespace(client)

        # Mock imports
        with patch.dict(
            "sys.modules",
            {
                "graphistry": namespace["graphistry"],
                "louieai": Mock(LouieClient=Mock(return_value=client)),
                "pandas": pd,
            },
        ):
            try:
                exec(code, namespace)
            except Exception as e:
                pytest.fail(
                    f"Code at {doc_file}:{line_num} failed:\n"
                    f"Error: {type(e).__name__}: {e}\n"
                    f"Code:\n{code}"
                )

    def test_index_examples(self):
        """Test examples in docs/index.md."""
        doc_path = Path("docs/index.md")
        if not doc_path.exists():
            pytest.skip("docs/index.md not found")

        blocks = extract_python_blocks(doc_path)
        for code, line_num, _context in blocks:
            self._test_code_block(code, "docs/index.md", line_num)

    def test_client_api_examples(self):
        """Test examples in docs/api/client.md."""
        doc_path = Path("docs/api/client.md")
        if not doc_path.exists():
            pytest.skip("docs/api/client.md not found")

        blocks = extract_python_blocks(doc_path)
        for code, line_num, _context in blocks:
            self._test_code_block(code, "docs/api/client.md", line_num)

    def test_query_patterns_examples(self):
        """Test examples in docs/query-patterns.md."""
        doc_path = Path("docs/query-patterns.md")
        if not doc_path.exists():
            pytest.skip("docs/query-patterns.md not found")

        blocks = extract_python_blocks(doc_path)
        for code, line_num, _context in blocks:
            self._test_code_block(code, "docs/query-patterns.md", line_num)


@pytest.mark.unit
@pytest.mark.parametrize(
    "doc_file",
    [
        "docs/index.md",
        "docs/api/client.md",
        "docs/query-patterns.md",
    ],
)
def test_documentation_file(doc_file):
    """Parametrized test for each documentation file."""
    doc_path = Path(doc_file)
    if not doc_path.exists():
        pytest.skip(f"{doc_file} not found")

    blocks = extract_python_blocks(doc_path)
    assert len(blocks) > 0, f"No Python code blocks found in {doc_file}"

    client = create_mock_client()
    namespace = create_test_namespace(client)

    failed = []
    for code, line_num, context in blocks:
        if should_skip_code(code):
            continue

        code = preprocess_code(code)

        with patch.dict(
            "sys.modules",
            {
                "graphistry": namespace["graphistry"],
                "louieai": Mock(LouieClient=Mock(return_value=client)),
                "pandas": pd,
            },
        ):
            try:
                exec(code, namespace)
            except Exception as e:
                failed.append((line_num, context, str(e)))

    if failed:
        msg = f"\n{len(failed)} code blocks failed in {doc_file}:\n"
        for line_num, context, error in failed:
            msg += f"  Line {line_num} ({context[:50]}...): {error}\n"
        pytest.fail(msg)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
