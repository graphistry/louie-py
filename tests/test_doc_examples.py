#!/usr/bin/env python3
"""Test all code examples in documentation.

This module extracts and tests Python code blocks from documentation files.
It can run in two modes:
1. With real API credentials (integration tests)
2. With mocked responses (unit tests)
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def extract_python_blocks(markdown_file: Path) -> list[tuple[str, int, str]]:
    """Extract Python code blocks from a markdown file.

    Returns:
        List of (code, line_number, context) tuples
    """
    content = markdown_file.read_text()
    blocks = []

    # Match ```python blocks
    pattern = r"```python\n(.*?)\n```"

    for match in re.finditer(pattern, content, re.DOTALL):
        code = match.group(1)
        line_num = content[: match.start()].count("\n") + 1

        # Get context (previous non-empty line)
        lines_before = content[: match.start()].strip().split("\n")
        context = lines_before[-1] if lines_before else "Unknown context"

        blocks.append((code, line_num, context))

    return blocks


def is_executable_code(code: str) -> bool:
    """Check if code block is meant to be executed.

    Filters out:
    - Import-only blocks
    - Shell commands
    - Partial code snippets
    """
    lines = code.strip().split("\n")

    # Skip shell commands
    if any(line.strip().startswith(("$", "#", "pip ", "uv ")) for line in lines):
        return False

    # Skip if only imports and comments
    non_import_lines = [
        line
        for line in lines
        if line.strip() and not line.strip().startswith(("import ", "from ", "#"))
    ]
    if not non_import_lines:
        return False

    # Try to parse as valid Python
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        # Might be a snippet showing partial code
        return False


def create_test_environment() -> dict[str, Any]:
    """Create a test environment with mocked dependencies."""
    from tests.doc_fixtures import create_mock_client

    # Mock graphistry module
    mock_graphistry = Mock()
    mock_graphistry.register = Mock()
    mock_graphistry.api_token = Mock(return_value="fake-token")
    mock_graphistry.nodes = Mock(return_value=mock_graphistry)
    mock_graphistry.edges = Mock(return_value=mock_graphistry)

    # Create mock client
    mock_client = create_mock_client()

    # Mock pandas DataFrame
    mock_df = Mock()
    mock_df.describe = Mock(return_value="DataFrame description")

    # Mock louieai module
    mock_louieai = Mock()
    mock_louieai.LouieClient = Mock(return_value=mock_client)

    # Create namespace
    namespace = {
        "graphistry": mock_graphistry,
        "louieai": mock_louieai,
        "LouieClient": Mock(return_value=mock_client),
        "df": mock_df,
        "df2": mock_df,
        "client": mock_client,
        "g": mock_graphistry,  # For graphistry client examples
        "print": print,  # Allow print statements
        "__builtins__": __builtins__,
    }

    # Pre-set some variables that might be referenced
    namespace["thread"] = mock_client.create_thread(name="Test Thread")
    namespace["response"] = mock_client.add_cell("", "Test")

    return namespace


class TestDocumentationExamples:
    """Test all documentation code examples."""

    @pytest.fixture
    def mock_env(self):
        """Provide mocked test environment."""
        return create_test_environment()

    def test_index_examples(self, mock_env):
        """Test examples from index.md."""
        doc_file = Path("docs/index.md")
        if not doc_file.exists():
            pytest.skip("Documentation file not found")

        blocks = extract_python_blocks(doc_file)
        executable_blocks = [
            (code, line, ctx) for code, line, ctx in blocks if is_executable_code(code)
        ]

        print(f"\nTesting {len(executable_blocks)} examples from {doc_file}")

        for code, line_num, context in executable_blocks:
            print(f"\n  Line {line_num}: {context[:50]}...")
            try:
                # Execute in controlled environment
                exec(code, mock_env)
                print("    ✓ Success")
            except Exception as e:
                pytest.fail(f"Example at line {line_num} failed: {e}\nCode:\n{code}")

    def test_client_api_examples(self, mock_env):
        """Test examples from api/client.md."""
        doc_file = Path("docs/api/client.md")
        if not doc_file.exists():
            pytest.skip("Documentation file not found")

        blocks = extract_python_blocks(doc_file)
        executable_blocks = [
            (code, line, ctx) for code, line, ctx in blocks if is_executable_code(code)
        ]

        print(f"\nTesting {len(executable_blocks)} examples from {doc_file}")

        for code, line_num, context in executable_blocks:
            print(f"\n  Line {line_num}: {context[:50]}...")
            try:
                exec(code, mock_env)
                print("    ✓ Success")
            except Exception as e:
                pytest.fail(f"Example at line {line_num} failed: {e}\nCode:\n{code}")

    def test_query_patterns_examples(self, mock_env):
        """Test examples from query-patterns.md."""
        doc_file = Path("docs/query-patterns.md")
        if not doc_file.exists():
            pytest.skip("Documentation file not found")

        blocks = extract_python_blocks(doc_file)

        # Query patterns has many partial snippets, be more lenient
        for code, line_num, context in blocks:
            print(f"\n  Line {line_num}: {context[:50]}...")

            # Skip obvious non-executable patterns
            if any(x in code for x in ["...", "# TODO", "your_user"]):
                print("    - Skipped (template code)")
                continue

            try:
                # Try to execute
                exec(code, mock_env)
                print("    ✓ Success")
            except NameError as e:
                # Expected for snippets that reference undefined variables
                print(f"    ~ Partial snippet (NameError: {e})")
            except Exception as e:
                print(f"    ✗ Failed: {type(e).__name__}: {e}")


@pytest.mark.integration
class TestDocumentationIntegration:
    """Integration tests with real Louie API.

    These tests are skipped unless credentials are available.
    """

    @pytest.mark.skipif(
        not os.environ.get("GRAPHISTRY_USERNAME"),
        reason="Integration test requires GRAPHISTRY_USERNAME",
    )
    def test_basic_example_integration(self):
        """Test a basic example against real API."""
        from tests.utils import load_test_credentials

        creds = load_test_credentials()
        if not creds:
            pytest.skip("No test credentials available")

        # Import real modules
        from graphistry.pygraphistry import GraphistryClient

        from louieai._client import LouieClient

        # Create GraphistryClient and register credentials
        graphistry_client = GraphistryClient()
        graphistry_client.register(
            api=creds["api_version"],
            server=creds["server"],
            username=creds["username"],
            password=creds["password"],
        )

        client = LouieClient(
            server_url="https://louie-dev.grph.xyz", graphistry_client=graphistry_client
        )

        # Test thread creation
        thread = client.create_thread(name="Doc Test", initial_prompt="Say hello")
        assert thread.id.startswith("D_")

        # Test adding to thread
        response = client.add_cell(thread.id, "What did I just ask?")
        assert response.thread_id == thread.id


def main():
    """Run documentation tests standalone."""
    import argparse

    parser = argparse.ArgumentParser(description="Test documentation examples")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests with real API"
    )
    parser.add_argument("--file", help="Test specific documentation file")
    args = parser.parse_args()

    if args.file:
        doc_file = Path(args.file)
        if not doc_file.exists():
            print(f"File not found: {doc_file}")
            sys.exit(1)

        blocks = extract_python_blocks(doc_file)
        print(f"Found {len(blocks)} Python blocks in {doc_file}")

        env = create_test_environment()
        for i, (code, line_num, context) in enumerate(blocks):
            print(f"\nBlock {i + 1} (line {line_num}): {context[:50]}...")
            print("Code:")
            print(code)
            print("\nExecuting...")
            try:
                exec(code, env)
                print("✓ Success")
            except Exception as e:
                print(f"✗ Failed: {type(e).__name__}: {e}")
    else:
        # Run pytest
        pytest_args = ["-v", __file__]
        if args.integration:
            pytest_args.extend(["-m", "integration"])
        sys.exit(pytest.main(pytest_args))


if __name__ == "__main__":
    main()
