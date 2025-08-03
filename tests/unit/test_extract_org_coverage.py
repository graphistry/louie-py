"""Tests to improve coverage of _extract_org_name_from_graphistry function."""

from unittest.mock import Mock

from louieai.__init__ import _extract_org_name_from_graphistry


class TestExtractOrgNameFromGraphistry:
    """Test the _extract_org_name_from_graphistry function."""

    def test_get_auth_info_method(self):
        """Test extracting org from get_auth_info method."""
        mock_client = Mock()
        # Make other methods fail/not exist
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None

        # Set up get_auth_info to return org
        mock_client.get_auth_info.return_value = {"org_name": "test-org-from-auth-info"}

        result = _extract_org_name_from_graphistry(mock_client)
        assert result == "test-org-from-auth-info"

    def test_get_auth_info_method_with_error(self):
        """Test get_auth_info method that raises exception."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        mock_client.get_auth_info.side_effect = Exception("Auth error")
        # Also make org_name fail
        del mock_client.org_name

        # Should not raise, just continue to next method
        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None

    def test_org_name_callable_method(self):
        """Test extracting org from org_name() callable method."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        mock_client.get_auth_info.side_effect = Exception("No auth info")

        # Set up org_name as callable
        mock_client.org_name = Mock(return_value="test-org-from-method")

        result = _extract_org_name_from_graphistry(mock_client)
        assert result == "test-org-from-method"

    def test_org_name_callable_with_error(self):
        """Test org_name() method that raises exception."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        mock_client.get_auth_info.side_effect = Exception("No auth info")
        mock_client.org_name = Mock(side_effect=Exception("Org error"))

        # Should not raise, just return None
        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None

    def test_no_org_methods_available(self):
        """Test when no org extraction methods work."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        # Remove the methods entirely
        del mock_client.get_auth_info
        del mock_client.org_name

        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None

    def test_magic_mock_filtering_in_auth_info(self):
        """Test that MagicMock values are filtered out from auth_info."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        mock_client.get_auth_info.return_value = {"org_name": "<MagicMock id='123'>"}
        # Also remove org_name to prevent fallback
        del mock_client.org_name

        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None

    def test_magic_mock_filtering_in_org_name_method(self):
        """Test that MagicMock values are filtered out from org_name()."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        mock_client.get_auth_info.side_effect = Exception("No auth info")
        mock_client.org_name = Mock(return_value="<MagicMock id='456'>")

        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None

    def test_auth_info_not_dict(self):
        """Test when get_auth_info returns non-dict."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        mock_client.get_auth_info.return_value = "not a dict"
        del mock_client.org_name

        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None

    def test_auth_info_missing_org_name(self):
        """Test when get_auth_info returns dict without org_name."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        mock_client.get_auth_info.return_value = {"other_field": "value"}
        del mock_client.org_name

        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None

    def test_empty_org_name_from_auth_info(self):
        """Test when get_auth_info returns empty org_name."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        mock_client.get_auth_info.return_value = {"org_name": ""}
        del mock_client.org_name

        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None

    def test_empty_org_name_from_callable(self):
        """Test when org_name() returns empty string."""
        mock_client = Mock()
        mock_client._credentials = None
        mock_client._auth_manager = None
        mock_client._org_name = None
        mock_client.get_auth_info.side_effect = Exception("No auth info")
        mock_client.org_name = Mock(return_value="")

        result = _extract_org_name_from_graphistry(mock_client)
        assert result is None
