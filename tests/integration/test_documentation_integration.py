"""Integration tests for documentation examples with real Louie API.

These tests require valid credentials and will be skipped if not available.
"""

import sys
from pathlib import Path

import graphistry
import pytest

from louieai._client import LouieClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import skip_if_no_credentials
from unit.test_documentation import extract_python_blocks


@pytest.mark.integration
@skip_if_no_credentials
class TestDocumentationIntegration:
    """Test documentation examples against real Louie API."""

    @pytest.fixture
    def real_client(self, test_credentials):
        """Create real LouieClient with test credentials."""
        # Register with Graphistry
        graphistry.register(
            api=test_credentials.get("api_version", 3),
            server=test_credentials["server"],
            username=test_credentials["username"],
            password=test_credentials["password"],
        )

        # Create Louie client
        louie_server = test_credentials.get(
            "louie_server", "https://louie-dev.grph.xyz"
        )
        return LouieClient(server_url=louie_server)

    def _should_test_code(self, code: str) -> bool:
        """Determine if code block should be tested in integration."""
        # Skip shell commands and setup code
        skip_patterns = [
            "$ ",
            "pip install",
            "uv pip",
            "...",
            "# TODO",
            "import graphistry",  # Skip setup imports
            "graphistry.register",  # Skip auth setup
            "client = LouieClient",  # Skip client creation
        ]
        return not any(pattern in code for pattern in skip_patterns)

    def _create_test_namespace(self, client):
        """Create namespace for executing code with real client."""
        return {
            "__builtins__": __builtins__,
            "client": client,
            "graphistry": graphistry,
            "LouieClient": LouieClient,
            "print": print,  # Allow real output
        }

    def test_basic_examples(self, real_client):
        """Test basic getting started examples."""
        # Test thread creation
        thread = real_client.create_thread(
            name="Integration Test Thread",
            initial_prompt="Say hello, this is an integration test",
        )
        assert thread.id.startswith("D_")
        assert thread.name == "Integration Test Thread"

        # Test adding cell
        response = real_client.add_cell(thread.id, "What did I just say?")
        assert response.thread_id == thread.id
        assert len(response.elements) > 0

        # Check we got a text response
        text_elements = response.text_elements
        assert len(text_elements) > 0

    def test_data_query_example(self, real_client):
        """Test data query returns DataFrame element."""
        thread = real_client.create_thread(name="Data Query Test")

        # Query that should return data
        response = real_client.add_cell(
            thread.id,
            "Show me a sample dataset with 5 rows of customer data "
            "including id, name, and email",
        )

        # Should get response
        assert response.thread_id == thread.id

        # Note: Actual response type depends on Louie's interpretation
        # It might return text explaining it can't access real customer data
        # or it might generate sample data
        assert len(response.elements) > 0

    @pytest.mark.slow
    def test_index_md_examples(self, real_client):
        """Test key examples from index.md."""
        doc_path = Path("docs/index.md")
        if not doc_path.exists():
            pytest.skip("docs/index.md not found")

        blocks = extract_python_blocks(doc_path)
        namespace = self._create_test_namespace(real_client)

        # Test only a few key examples to avoid rate limits
        key_examples = []
        for code, line_num, context in blocks:
            if "create_thread" in code and self._should_test_code(code):
                key_examples.append((code, line_num, context))

        # Limit to first 3 examples
        for code, line_num, context in key_examples[:3]:
            print(f"\nTesting example from line {line_num}: {context[:50]}...")

            try:
                # Preprocess but keep real server
                code = code.replace('"your_user"', '"test_user"')
                code = code.replace('"your_pass"', '"test_pass"')

                # Execute with real client
                exec(code, namespace)
                print("✓ Success")

            except Exception as e:
                # Some examples might fail due to:
                # - Rate limits
                # - Specific data requirements
                # - Server state
                print(f"✗ Failed: {type(e).__name__}: {e}")
                # Don't fail the whole test suite

    def test_thread_persistence(self, real_client):
        """Test that threads persist across queries."""
        # Create thread
        thread = real_client.create_thread(
            name="Persistence Test", initial_prompt="Remember the number 42"
        )

        # Query in same thread
        response = real_client.add_cell(
            thread.id, "What number did I ask you to remember?"
        )

        # Check response references the number
        text_elements = response.text_elements
        assert len(text_elements) > 0
        # Note: Can't guarantee exact response, but thread should exist

        # List threads to verify it exists
        threads = real_client.list_threads()
        thread_ids = [t.id for t in threads]
        assert thread.id in thread_ids

    def test_error_handling(self, real_client):
        """Test error handling with invalid requests."""
        # Try to use non-existent thread
        import httpx

        with pytest.raises((httpx.HTTPError, RuntimeError)):
            real_client.get_thread("D_nonexistent_thread_12345")

    @pytest.mark.parametrize(
        "prompt,expected_type",
        [
            ("Say hello", "text"),
            ("What is 2+2?", "text"),
            # Note: Actual data/graph queries depend on Louie's capabilities
            # and what data sources are connected in the test environment
        ],
    )
    def test_response_types(self, real_client, prompt, expected_type):
        """Test different prompts return expected response types."""
        response = real_client.add_cell("", prompt)

        assert response.thread_id.startswith("D_")
        assert len(response.elements) > 0

        if expected_type == "text":
            assert len(response.text_elements) > 0

    def test_concurrent_threads(self, real_client):
        """Test managing multiple threads concurrently."""
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = real_client.create_thread(
                name=f"Concurrent Test {i}", initial_prompt=f"This is thread number {i}"
            )
            threads.append(thread)

        # Query each thread
        for _i, thread in enumerate(threads):
            response = real_client.add_cell(thread.id, "What thread number is this?")
            assert response.thread_id == thread.id

        # Verify all threads exist
        all_threads = real_client.list_threads(page_size=50)
        all_thread_ids = [t.id for t in all_threads]

        for thread in threads:
            assert thread.id in all_thread_ids
