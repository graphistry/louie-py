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


def extract_python_blocks(markdown_path: Path):
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
        'lui("',  # Skip code blocks with actual lui calls that make HTTP requests
        "lui.text",  # Skip property access that might fail after HTTP calls
        "lui.df",  # Skip property access that might fail after HTTP calls
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

    # Create a properly mocked graphistry client with auth manager
    mock_registered_client = Mock()
    mock_registered_client._auth_manager = Mock()
    mock_registered_client._auth_manager._credentials = {
        "username": "test_user",
        "password": "test_password",
        "api_key": "test_api_key",
        "personal_key_id": "test_personal_key_id",
        "personal_key_secret": "test_personal_key_secret",
        "org_name": "test_org",
        "api": 3,
        "server": "test.graphistry.com",
    }
    mock_registered_client._auth_manager.get_token.return_value = "fake-token-123"

    mock_graphistry.register = Mock(return_value=mock_registered_client)
    mock_graphistry.api_token = Mock(return_value="fake-token")
    mock_graphistry.nodes = Mock(return_value=mock_graphistry)
    mock_graphistry.edges = Mock(return_value=mock_graphistry)

    # Mock louieai module
    mock_louieai = Mock()
    mock_louieai.LouieClient = Mock(return_value=client)

    # Create some pre-existing objects that snippets might reference
    thread = client.create_thread(name="Test Thread")
    response = client.add_cell(thread.id, "test query")
    response1 = client.add_cell(thread.id, "query data")  # Will be dataframe type
    response2 = client.add_cell(thread.id, "analyze results")

    # Ensure response1 has a working to_dataframe method for chaining examples
    if not hasattr(response1, "to_dataframe") or response1.to_dataframe() is None:
        response1.to_dataframe = Mock(return_value=MockDataFrame())

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
        "thread_id": thread.id,  # Add thread_id for code examples
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
        "g": mock_registered_client,
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

        # Create a mock lui object
        mock_lui = Mock()
        mock_lui.text = "Mocked text response"
        mock_lui.df = pd.DataFrame({"col1": [1, 2, 3]})
        mock_lui.dfs = [mock_lui.df]
        mock_lui.texts = [mock_lui.text]
        mock_lui.elements = []
        mock_lui.errors = []
        mock_lui.has_errors = False
        mock_lui._client = client  # Add the client reference
        mock_lui.traces = False  # Add traces property

        # Mock lui as callable
        def mock_lui_call(*args, **kwargs):
            return Mock(text="Response", df=mock_lui.df)

        mock_lui.side_effect = mock_lui_call

        # Create mock louie function that returns mock_lui
        def mock_louie_factory(*args, **kwargs):
            return mock_lui

        # Add the mock louieai function directly to namespace
        namespace["louieai"] = mock_louie_factory

        # Mock environment variables and graphistry module
        with (
            patch.dict(
                "os.environ",
                {
                    "GRAPHISTRY_USERNAME": "test_user",
                    "GRAPHISTRY_PASSWORD": "test_password",
                    "GRAPHISTRY_SERVER": "test.graphistry.com",
                },
            ),
            patch.dict(
                "sys.modules",
                {
                    "graphistry": namespace["graphistry"],
                    "graphistry.pygraphistry": Mock(GraphistryClient=Mock),
                },
            ),
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
        """Test examples in docs/guides/query-patterns.md."""
        doc_path = Path("docs/guides/query-patterns.md")
        if not doc_path.exists():
            pytest.skip("docs/guides/query-patterns.md not found")

        blocks = extract_python_blocks(doc_path)
        for code, line_num, _context in blocks:
            self._test_code_block(code, "docs/guides/query-patterns.md", line_num)


@pytest.mark.unit
@pytest.mark.parametrize(
    "doc_file",
    [
        "docs/getting-started/quick-start.md",
        "docs/api/client.md",
        "docs/guides/query-patterns.md",
        "docs/guides/examples.md",
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

        # Create a comprehensive mock lui object
        mock_lui = _create_comprehensive_mock_lui(client)

        # Add lui to namespace for notebook API code
        namespace["lui"] = mock_lui

        # Create mock louie factory that returns mock_lui
        def mock_louie_factory(*args, mock_lui=mock_lui, **kwargs):
            return mock_lui

        with patch.dict(
            "sys.modules",
            {
                "graphistry": namespace["graphistry"],
                "louieai": Mock(
                    LouieClient=Mock(return_value=client),
                    louie=mock_louie_factory,
                    Cursor=Mock,
                ),
                "louieai.notebook": Mock(lui=mock_lui),
                "louieai.globals": Mock(lui=mock_lui),
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


def _create_comprehensive_mock_lui(client=None):
    """Create a comprehensive mock lui object that works like the real one."""
    mock_lui = Mock()

    # Create client if not provided
    if client is None:
        client = create_mock_client()
    mock_lui._client = client

    # Basic attributes
    mock_lui.text = "Mocked text response"
    mock_df = pd.DataFrame(
        {
            "region": ["North", "South", "East", "West", "North"],
            "sales": [100, 200, 150, 300, 250],
            "product": ["A", "B", "C", "D", "E"],
            "country": ["USA", "Canada", "Mexico", "USA", "Canada"],
            "failed_logins": [5, 3, 8, 2, 1],
            "col1": [1, 2, 3, 4, 5],
        }
    )
    mock_lui.df = mock_df
    mock_lui.dfs = [mock_df]  # Make it a real list
    mock_lui.texts = ["Mocked text response"]
    mock_lui.elements = []
    mock_lui.errors = []
    mock_lui.has_errors = False
    mock_lui.traces = False

    # Add history attribute for accessing previous results
    mock_history = []
    for i in range(5):  # Create some mock history
        hist_item = Mock()
        hist_item.text = f"Historical text {i}"
        hist_item.df = mock_df
        hist_item.dfs = [mock_df]
        hist_item.texts = [f"Historical text {i}"]
        mock_history.append(hist_item)
    mock_lui.history = mock_history

    # Make lui callable
    def mock_lui_call(*args, **kwargs):
        response = Mock()
        response.text = "Response text"
        response.df = mock_df
        response.dfs = [mock_df]
        response.texts = ["Response text"]
        response.text_elements = [{"type": "TextElement", "content": "Response text"}]
        response.dataframe_elements = [{"type": "DfElement", "table": mock_df}]
        # Update lui's state
        mock_lui.text = response.text
        mock_lui.df = response.df
        return response

    # Use __call__ instead of side_effect for better control
    mock_lui.__call__ = mock_lui_call

    # Make lui subscriptable for history
    # Create a mock history response that will be returned for any index
    hist_response = Mock()
    hist_response.text = "Historical text"
    hist_response.df = pd.DataFrame(
        {
            "region": ["North", "South"],
            "sales": [100, 200],
            "product": ["A", "B"],
            "col1": [1, 2],
        }
    )
    hist_response.dfs = [hist_response.df]
    hist_response.texts = ["Historical text"]

    # Configure the mock to support indexing
    mock_lui.__getitem__ = Mock(return_value=hist_response)

    return mock_lui


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
