"""Tests for Cursor.new() method and thread naming functionality."""

from unittest.mock import Mock, patch

import pytest

from louieai._client import LouieClient
from louieai.notebook import Cursor


class TestCursorNew:
    """Test the Cursor.new() method functionality."""

    def test_new_preserves_client(self):
        """Test that new() preserves the entire client instance."""
        # Create a mock client with specific attributes
        mock_client = Mock(spec=LouieClient)
        mock_client.server_url = "https://test.louie.ai"
        mock_client._timeout = 600
        mock_client._streaming_timeout = 180
        mock_client._auth_manager = Mock()
        mock_client._auth_manager._credentials = {"org_name": "test-org"}

        # Create parent cursor
        parent = Cursor(client=mock_client, share_mode="Organization")

        # Create new cursor
        new_cursor = parent.new()

        # Verify client is preserved (same instance)
        assert new_cursor._client is parent._client
        assert new_cursor._client.server_url == "https://test.louie.ai"
        assert new_cursor._client._timeout == 600
        assert new_cursor._client._streaming_timeout == 180

    def test_new_inherits_share_mode(self):
        """Test that new() inherits share_mode from parent if not specified."""
        mock_client = Mock(spec=LouieClient)

        # Test each share mode
        for mode in ["Private", "Organization", "Public"]:
            parent = Cursor(client=mock_client, share_mode=mode)
            new_cursor = parent.new()
            assert new_cursor._share_mode == mode

    def test_new_override_share_mode(self):
        """Test that new() can override share_mode."""
        mock_client = Mock(spec=LouieClient)
        parent = Cursor(client=mock_client, share_mode="Organization")

        # Override to Private
        new_cursor = parent.new(share_mode="Private")
        assert new_cursor._share_mode == "Private"
        assert parent._share_mode == "Organization"  # Parent unchanged

    def test_new_with_name(self):
        """Test that new() accepts and stores name parameter."""
        mock_client = Mock(spec=LouieClient)
        parent = Cursor(client=mock_client)

        new_cursor = parent.new(name="Test Analysis")
        assert new_cursor._name == "Test Analysis"
        assert parent._name is None  # Parent has no name

    def test_new_fresh_thread(self):
        """Test that new() creates a fresh thread (no thread_id)."""
        mock_client = Mock(spec=LouieClient)
        parent = Cursor(client=mock_client)
        parent._current_thread = "existing-thread-id"

        new_cursor = parent.new()
        assert new_cursor._current_thread is None
        assert parent._current_thread == "existing-thread-id"

    def test_new_empty_history(self):
        """Test that new() starts with empty history."""
        mock_client = Mock(spec=LouieClient)
        parent = Cursor(client=mock_client)
        # Simulate some history
        parent._history.append(Mock())
        parent._history.append(Mock())

        new_cursor = parent.new()
        assert len(new_cursor._history) == 0
        assert len(parent._history) == 2

    def test_new_invalid_share_mode(self):
        """Test that new() validates share_mode parameter."""
        mock_client = Mock(spec=LouieClient)
        parent = Cursor(client=mock_client)

        with pytest.raises(ValueError) as exc_info:
            parent.new(share_mode="InvalidMode")

        assert "Invalid share_mode: 'InvalidMode'" in str(exc_info.value)
        assert "Must be one of: Organization, Private, Public" in str(exc_info.value)


class TestCursorShareModeValidation:
    """Test share_mode validation in Cursor.__init__."""

    def test_valid_share_modes(self):
        """Test that valid share modes are accepted."""
        mock_client = Mock(spec=LouieClient)

        for mode in ["Private", "Organization", "Public"]:
            cursor = Cursor(client=mock_client, share_mode=mode)
            assert cursor._share_mode == mode

    def test_invalid_share_mode_init(self):
        """Test that invalid share mode raises ValueError."""
        mock_client = Mock(spec=LouieClient)

        with pytest.raises(ValueError) as exc_info:
            Cursor(client=mock_client, share_mode="public")  # lowercase

        assert "Invalid share_mode: 'public'" in str(exc_info.value)

    def test_invalid_share_mode_empty(self):
        """Test that empty share mode raises ValueError."""
        mock_client = Mock(spec=LouieClient)

        with pytest.raises(ValueError) as exc_info:
            Cursor(client=mock_client, share_mode="")

        assert "Invalid share_mode: ''" in str(exc_info.value)


class TestCursorNameHandling:
    """Test thread name handling functionality."""

    def test_louie_factory_with_name(self):
        """Test that louie() factory passes name to Cursor."""
        from louieai import louie

        with patch("louieai._client.LouieClient") as mock_client_class:
            mock_client = Mock(spec=LouieClient)
            mock_client_class.return_value = mock_client

            cursor = louie(username="test", password="test_pass", name="My Analysis")
            assert cursor._name == "My Analysis"

    def test_cursor_init_with_name(self):
        """Test that Cursor stores name from init."""
        mock_client = Mock(spec=LouieClient)
        cursor = Cursor(client=mock_client, name="Test Thread")
        assert cursor._name == "Test Thread"

    def test_name_auto_generation(self):
        """Test that name is auto-generated from first message if not provided."""
        mock_client = Mock(spec=LouieClient)
        mock_client.add_cell = Mock(return_value=Mock(thread_id="new-thread"))

        cursor = Cursor(client=mock_client)
        assert cursor._name is None

        # Simulate first call - should auto-generate name
        with patch.object(cursor, "_in_jupyter", return_value=False):
            cursor("What are the top 10 customers by revenue?")

        # Name should be generated from prompt
        assert cursor._name == "What are the top 10 customers by revenue?"

        # Test with long prompt
        cursor2 = Cursor(client=mock_client)
        with patch.object(cursor2, "_in_jupyter", return_value=False):
            cursor2(
                "This is a very long prompt that exceeds fifty characters and "
                "should be truncated with ellipsis"
            )

        assert cursor2._name == "This is a very long prompt that exceeds fifty char..."
        assert len(cursor2._name) == 53  # 50 chars + "..."

    def test_name_not_overwritten(self):
        """Test that existing name is not overwritten on first message."""
        mock_client = Mock(spec=LouieClient)
        mock_client.add_cell = Mock(return_value=Mock(thread_id="new-thread"))

        cursor = Cursor(client=mock_client, name="Predefined Name")

        with patch.object(cursor, "_in_jupyter", return_value=False):
            cursor("Some query")

        # Name should remain as predefined
        assert cursor._name == "Predefined Name"


class TestCursorChaining:
    """Test that multiple new() calls work correctly."""

    def test_chained_new_calls(self):
        """Test creating multiple new cursors from parent and each other."""
        mock_client = Mock(spec=LouieClient)

        # Create parent
        parent = Cursor(client=mock_client, share_mode="Organization", name="Parent")

        # Create child1 from parent
        child1 = parent.new(share_mode="Private", name="Child 1")
        assert child1._client is parent._client
        assert child1._share_mode == "Private"
        assert child1._name == "Child 1"

        # Create child2 from child1
        child2 = child1.new(name="Child 2")  # Inherits Private from child1
        assert child2._client is parent._client
        assert child2._share_mode == "Private"
        assert child2._name == "Child 2"

        # Create child3 from parent with inherited settings
        child3 = parent.new()
        assert child3._client is parent._client
        assert child3._share_mode == "Organization"  # Inherited from parent
        assert child3._name is None  # No name specified
