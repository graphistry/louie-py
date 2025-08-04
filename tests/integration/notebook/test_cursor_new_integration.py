"""Integration tests for Cursor.new() method with mocked API responses."""

from unittest.mock import Mock, create_autospec, patch

import pytest

from louieai._client import LouieClient
from louieai.notebook import Cursor


class TestCursorNewIntegration:
    """Integration tests for Cursor.new() with realistic scenarios."""

    def test_new_creates_independent_threads(self):
        """Test that new() creates truly independent conversation threads."""
        # Create mock client
        mock_client = create_autospec(LouieClient, instance=True)

        # Mock add_cell responses
        mock_client.add_cell.side_effect = [
            Mock(thread_id="thread-1"),  # First call
            Mock(thread_id="thread-2"),  # Second call
        ]

        # Create parent cursor with mock client
        parent = Cursor(client=mock_client, share_mode="Organization")

        # First query creates thread-1
        with patch.object(parent, "_in_jupyter", return_value=False):
            parent("First conversation")
        assert parent._current_thread == "thread-1"

        # Create new cursor - should get different thread
        child = parent.new(share_mode="Private")

        # Second query creates thread-2
        with patch.object(child, "_in_jupyter", return_value=False):
            child("Second conversation")

        assert child._current_thread == "thread-2"
        assert parent._current_thread == "thread-1"  # Parent unchanged

        # Verify share modes
        assert parent._share_mode == "Organization"
        assert child._share_mode == "Private"

        # Verify both use same client
        assert child._client is parent._client

    def test_new_preserves_auth_through_queries(self):
        """Test that new() preserves authentication through multiple queries."""
        # Create mock client with auth manager
        mock_client = create_autospec(LouieClient, instance=True)
        mock_client._auth_manager = Mock()
        mock_client._auth_manager._credentials = {
            "personal_key_id": "pk_123",
            "personal_key_secret": "sk_456",
            "org_name": "test-org",
        }
        mock_client._timeout = 600
        mock_client._streaming_timeout = 180

        # Create parent cursor
        parent = Cursor(client=mock_client, share_mode="Organization")

        # Create multiple new cursors
        child1 = parent.new()
        child2 = child1.new()

        # All should share same client
        assert child1._client is parent._client
        assert child2._client is parent._client

        # Verify auth preserved
        assert child2._client._auth_manager._credentials["personal_key_id"] == "pk_123"
        assert child2._client._auth_manager._credentials["org_name"] == "test-org"

        # Verify timeouts preserved
        assert child2._client._timeout == 600
        assert child2._client._streaming_timeout == 180

    def test_name_generation_from_first_message(self):
        """Test that thread names are auto-generated from first message."""
        # Create mock client
        mock_client = create_autospec(LouieClient, instance=True)
        mock_client.add_cell.return_value = Mock(thread_id="thread-1")

        # Create cursor without name
        cursor = Cursor(client=mock_client)
        assert cursor._name is None

        # First query should set name
        with patch.object(cursor, "_in_jupyter", return_value=False):
            cursor("Analyze customer churn data")
        assert cursor._name == "Analyze customer churn data"

        # Create new cursor with explicit name
        cursor2 = cursor.new(name="Churn Analysis v2")
        assert cursor2._name == "Churn Analysis v2"

        # First query should NOT override explicit name
        mock_client.add_cell.return_value = Mock(thread_id="thread-2")
        with patch.object(cursor2, "_in_jupyter", return_value=False):
            cursor2("Different query")
        assert cursor2._name == "Churn Analysis v2"  # Unchanged

    def test_streaming_integration_with_new_cursors(self):
        """Test that streaming responses work correctly with new() cursors."""
        # Create mock client
        mock_client = create_autospec(LouieClient, instance=True)

        # Create parent cursor
        parent = Cursor(client=mock_client, share_mode="Private")

        # Mock Jupyter environment and streaming
        with (
            patch.object(parent, "_in_jupyter", return_value=True),
            patch("louieai.notebook.streaming.stream_response") as mock_stream_response,
        ):
            # Mock streaming result
            mock_stream_response.return_value = {
                "dthread_id": "thread-1",
                "elements": [
                    {"type": "TextElement", "content": "Analysis complete"},
                ],
            }

            parent("Run analysis")

            # Verify streaming was called with correct params
            mock_stream_response.assert_called_once_with(
                parent._client,
                thread_id="",
                prompt="Run analysis",
                agent="LouieAgent",
                traces=False,
                share_mode="Private",
            )

        # Create new cursor with different share_mode
        child = parent.new(share_mode="Organization")

        # Test streaming with new cursor
        with (
            patch.object(child, "_in_jupyter", return_value=True),
            patch("louieai.notebook.streaming.stream_response") as mock_stream_response,
        ):
            mock_stream_response.return_value = {
                "dthread_id": "thread-2",
                "elements": [],
            }

            child("New analysis")

            # Verify new cursor uses correct share_mode
            mock_stream_response.assert_called_once_with(
                child._client,
                thread_id="",
                prompt="New analysis",
                agent="LouieAgent",
                traces=False,
                share_mode="Organization",  # Inherited from new()
            )

    def test_error_handling_preserved_in_new(self):
        """Test that error handling configuration is preserved in new()."""
        # Create mock client with custom timeouts
        mock_client = create_autospec(LouieClient, instance=True)
        mock_client._timeout = 600  # 10 minutes
        mock_client._streaming_timeout = 180  # 3 minutes
        mock_client.server_url = "https://custom.louie.ai"

        # Create cursor
        cursor = Cursor(client=mock_client)

        # Create new cursor
        new_cursor = cursor.new()

        # Client settings should be preserved
        assert new_cursor._client._timeout == 600
        assert new_cursor._client._streaming_timeout == 180
        assert new_cursor._client.server_url == "https://custom.louie.ai"


class TestShareModeScenarios:
    """Test various share_mode inheritance and override scenarios."""

    def test_share_mode_inheritance_chain(self):
        """Test share_mode inheritance through multiple new() calls."""
        # Mock client
        mock_client = create_autospec(LouieClient, instance=True)

        # Start with Organization
        org_cursor = Cursor(client=mock_client, share_mode="Organization")

        # Create Private child
        private_cursor = org_cursor.new(share_mode="Private")
        assert private_cursor._share_mode == "Private"

        # Create child that inherits Private
        inherited_cursor = private_cursor.new()
        assert inherited_cursor._share_mode == "Private"

        # Create Public child from Private parent
        public_cursor = private_cursor.new(share_mode="Public")
        assert public_cursor._share_mode == "Public"

        # Original unchanged
        assert org_cursor._share_mode == "Organization"

    def test_invalid_share_mode_in_new(self):
        """Test that invalid share_mode in new() raises appropriate error."""
        mock_client = create_autospec(LouieClient, instance=True)
        cursor = Cursor(client=mock_client)

        # Test various invalid modes
        invalid_modes = ["private", "PUBLIC", "Org", "Team", ""]

        for invalid_mode in invalid_modes:
            with pytest.raises(ValueError) as exc_info:
                cursor.new(share_mode=invalid_mode)
            assert "Invalid share_mode" in str(exc_info.value)
            assert "Must be one of: Organization, Private, Public" in str(
                exc_info.value
            )

    def test_none_share_mode_inherits(self):
        """Test that None share_mode inherits from parent."""
        mock_client = create_autospec(LouieClient, instance=True)

        parent = Cursor(client=mock_client, share_mode="Public")
        child = parent.new(share_mode=None)

        assert child._share_mode == "Public"  # Inherited
