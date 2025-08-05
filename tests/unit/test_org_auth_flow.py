#!/usr/bin/env python3
"""Test org_name authentication flow to detect confused deputy problem."""

from unittest.mock import MagicMock, Mock, patch

import pytest

import louieai
from louieai._client import LouieClient
from louieai.auth import AuthManager


class TestOrgAuthFlow:
    """Test organization authentication flow."""

    def test_direct_client_org_name_flow(self):
        """Test that LouieClient correctly handles org_name parameter."""
        target_org = "databricks-pat-botsv3"

        # Mock PyGraphistry client
        mock_graphistry = MagicMock()
        mock_graphistry.api_token.return_value = "fake-jwt-token-123"

        with patch("louieai.auth.GraphistryClient", return_value=mock_graphistry):
            client = LouieClient(
                personal_key_id="CU5V6VZJB7",
                personal_key_secret="32RBP6PUCSUVAIYJ",
                org_name=target_org,
                server="graphistry-dev.grph.xyz",
                server_url="https://louie-dev.grph.xyz",
            )

            # Verify org_name is stored in credentials
            assert client._auth_manager._credentials["org_name"] == target_org

            # Verify org_name appears in headers
            headers = client._get_headers()
            assert "X-Graphistry-Org" in headers
            assert headers["X-Graphistry-Org"] == target_org

    def test_louie_factory_with_graphistry_client_confused_deputy(self):
        """Test the confused deputy problem: louie() factory loses org_name from
        pre-registered graphistry."""
        target_org = "databricks-pat-botsv3"

        # Mock a pre-registered PyGraphistry client (simulating user's scenario)
        mock_graphistry = MagicMock()
        mock_graphistry.api_token.return_value = "fake-jwt-token-123"

        # Simulate different ways graphistry might store org_name
        mock_graphistry._org_name = target_org
        mock_graphistry._credentials = {"org_name": target_org}

        mock_auth_mgr = MagicMock()
        mock_auth_mgr._credentials = {"org_name": target_org}
        mock_graphistry._auth_manager = mock_auth_mgr

        # Test the louie() factory function with pre-registered graphistry
        lui = louieai.louie(
            graphistry_client=mock_graphistry,
            server_url="https://louie-dev.grph.xyz",
            share_mode="Private",
        )

        # Check what org_name the LouieAI client has
        auth_manager = lui._client._auth_manager
        stored_org = auth_manager._credentials.get("org_name")

        # This is the key test: Does LouieAI extract org from existing
        # graphistry client?
        if stored_org != target_org:
            pytest.fail(
                f"CONFUSED DEPUTY DETECTED: "
                f"Expected org_name='{target_org}', but LouieAI client has "
                f"'{stored_org}'. "
                f"This means API calls will be made with wrong organization context!"
            )

        # Verify API headers would include correct org
        headers = lui._client._get_headers()
        if "X-Graphistry-Org" not in headers:
            pytest.fail(
                "CONFUSED DEPUTY DETECTED: "
                "No X-Graphistry-Org header found. API calls will be made as "
                "'personal' instead of specified org!"
            )

        if headers["X-Graphistry-Org"] != target_org:
            pytest.fail(
                f"CONFUSED DEPUTY DETECTED: "
                f"Wrong org in headers. Expected '{target_org}', got "
                f"'{headers['X-Graphistry-Org']}'"
            )

    def test_org_slug_conversion(self):
        """Test that org names are properly converted to slug format."""
        test_cases = [
            ("My Organization", "my-organization"),
            ("databricks-pat-botsv3", "databricks-pat-botsv3"),
            ("Test_Org-123", "test-org-123"),
            ("UPPERCASE ORG", "uppercase-org"),
            ("Org with Special@#$%", "org-with-special"),
        ]

        mock_graphistry = MagicMock()
        mock_graphistry.api_token.return_value = "fake-token"

        with patch("louieai.auth.GraphistryClient", return_value=mock_graphistry):
            for org_input, expected_slug in test_cases:
                client = LouieClient(
                    personal_key_id="test_key",
                    personal_key_secret="test_secret",
                    org_name=org_input,
                    server_url="https://test.louie.ai",
                )

                headers = client._get_headers()
                assert headers["X-Graphistry-Org"] == expected_slug, (
                    f"org_name '{org_input}' should become slug '{expected_slug}', "
                    f"got '{headers['X-Graphistry-Org']}'"
                )

    def test_auth_manager_org_passthrough(self):
        """Test that AuthManager correctly passes org_name to PyGraphistry register."""
        target_org = "test-organization"

        mock_graphistry = MagicMock()
        mock_graphistry.api_token.return_value = None  # Force auth refresh

        # Track calls to register
        register_calls = []

        def track_register(**kwargs):
            register_calls.append(kwargs)
            return mock_graphistry

        mock_graphistry.register = Mock(side_effect=track_register)

        auth_manager = AuthManager(
            graphistry_client=mock_graphistry,
            personal_key_id="test_key",
            personal_key_secret="test_secret",
            org_name=target_org,
        )

        # Force auth refresh (which should call register)
        auth_manager._refresh_auth()

        # Verify org_name was passed to PyGraphistry register
        assert len(register_calls) == 1, (
            "Expected exactly one call to graphistry.register()"
        )

        register_kwargs = register_calls[0]
        assert "org_name" in register_kwargs, (
            "org_name should be passed to graphistry.register()"
        )
        assert register_kwargs["org_name"] == target_org, (
            f"Expected org_name='{target_org}', got '{register_kwargs['org_name']}'"
        )

    @pytest.mark.skip(
        reason="This test demonstrates the confused deputy problem - will fail "
        "until fixed"
    )
    def test_reproduction_of_user_scenario(self):
        """Reproduce the exact user scenario to demonstrate the confused deputy
        problem."""

        # Step 1: User registers with PyGraphistry including org_name
        with patch("graphistry.register") as mock_g_register:
            mock_registered_client = MagicMock()
            mock_registered_client.api_token.return_value = "user-jwt-token"
            mock_g_register.return_value = mock_registered_client

            # Simulate: g = graphistry.register(org_name='databricks-pat-botsv3', ...)
            g = mock_registered_client

            # Step 2: User creates LouieAI interface with the registered client
            lui = louieai.louie(
                g, server_url="https://louie-dev.grph.xyz", share_mode="Private"
            )

            # Step 3: User makes a query - this should use the correct org
            # But due to confused deputy problem, it might not

            # Check what org context the LouieAI client will use
            auth_manager = lui._client._auth_manager
            stored_org = auth_manager._credentials.get("org_name")

            # This should be 'databricks-pat-botsv3' but is likely None
            assert stored_org == "databricks-pat-botsv3", (
                f"Confused deputy: Expected 'databricks-pat-botsv3', got '{stored_org}'"
            )

            # Check headers that would be sent to LouieAI API
            headers = lui._client._get_headers()
            assert "X-Graphistry-Org" in headers, (
                "Missing org header - API calls will be made as 'personal'"
            )

            assert headers["X-Graphistry-Org"] == "databricks-pat-botsv3", (
                f"Wrong org in API headers: {headers.get('X-Graphistry-Org')}"
            )
