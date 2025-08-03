"""Test import error handling and edge cases in __init__.py"""

import sys
from unittest.mock import Mock, patch


class TestVersionImportError:
    """Test version import error handling."""

    def test_version_import_error(self):
        """Test fallback when _version module is not available."""
        # Save the original module
        original_modules = dict(sys.modules)

        try:
            # Remove the _version module if it exists
            if "louieai._version" in sys.modules:
                del sys.modules["louieai._version"]
            if "louieai" in sys.modules:
                del sys.modules["louieai"]

            # Mock the import to fail
            with patch.dict("sys.modules", {"louieai._version": None}):
                # Import louieai - this should trigger the fallback
                import louieai

                assert louieai.__version__ == "0.0.0+unknown"
        finally:
            # Restore original modules
            sys.modules.update(original_modules)


class TestExtractOrgNameEdgeCases:
    """Test edge cases in _extract_org_name_from_graphistry."""

    def test_none_graphistry_client(self):
        """Test with None client."""
        from louieai.__init__ import _extract_org_name_from_graphistry

        result = _extract_org_name_from_graphistry(None)
        assert result is None

    def test_auth_manager_with_org_name(self):
        """Test extracting org from auth_manager credentials."""
        from louieai.__init__ import _extract_org_name_from_graphistry

        mock_client = Mock()
        mock_client._credentials = None  # No direct credentials

        # Set up auth_manager with credentials
        mock_auth_manager = Mock()
        mock_auth_manager._credentials = {"org_name": "test-org-from-auth-manager"}
        mock_client._auth_manager = mock_auth_manager

        # Make sure other methods don't exist/fail
        mock_client._org_name = None
        del mock_client.get_auth_info
        del mock_client.org_name

        result = _extract_org_name_from_graphistry(mock_client)
        assert result == "test-org-from-auth-manager"

    def test_auth_manager_with_magic_mock_org(self):
        """Test that MagicMock values in auth_manager are filtered."""
        from louieai.__init__ import _extract_org_name_from_graphistry

        mock_client = Mock()
        mock_client._credentials = None

        # Set up auth_manager with MagicMock org_name
        mock_auth_manager = Mock()
        mock_auth_manager._credentials = {"org_name": "<MagicMock id='789'>"}
        mock_client._auth_manager = mock_auth_manager

        # Make sure other methods don't exist/fail
        mock_client._org_name = None
        del mock_client.get_auth_info
        del mock_client.org_name

        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None

    def test_auth_manager_empty_org_name(self):
        """Test auth_manager with empty org_name."""
        from louieai.__init__ import _extract_org_name_from_graphistry

        mock_client = Mock()
        mock_client._credentials = None

        # Set up auth_manager with empty org_name
        mock_auth_manager = Mock()
        mock_auth_manager._credentials = {"org_name": ""}
        mock_client._auth_manager = mock_auth_manager

        # Make sure other methods don't exist/fail
        mock_client._org_name = None
        del mock_client.get_auth_info
        del mock_client.org_name

        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None
