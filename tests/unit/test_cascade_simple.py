#!/usr/bin/env python3
"""Simple test to verify org_name cascade fix."""

import os
from unittest.mock import patch

import louieai


class TestSimpleCascade:
    """Simple test for org_name cascade."""

    def test_user_scenario_fixed(self):
        """Test the exact user scenario that was broken."""
        target_org = "databricks-pat-botsv3"

        # Create a simple mock that doesn't auto-generate attributes
        class MockGraphistry:
            def __init__(self):
                self._credentials = {"org_name": target_org}

            def api_token(self):
                return "fake-token"

        mock_g = MockGraphistry()

        with patch("graphistry.pygraphistry.GraphistryClient", return_value=mock_g):
            # User's original code that was broken:
            lui = louieai.louie(
                mock_g, server_url="https://louie-dev.grph.xyz", share_mode="Private"
            )

            # Check if org was extracted correctly
            stored_org = lui._client._auth_manager._credentials.get("org_name")
            print(f"Stored org: {stored_org}")

            assert stored_org == target_org, (
                f"STILL BROKEN: expected '{target_org}', got '{stored_org}'"
            )

            # Check API headers
            headers = lui._client._get_headers()
            print(f"Headers: {headers}")

            assert "X-Graphistry-Org" in headers, "Missing org header"
            assert headers["X-Graphistry-Org"] == target_org, (
                f"Wrong org header: {headers['X-Graphistry-Org']}"
            )

    def test_explicit_parameter_wins(self):
        """Test that explicit org_name parameter takes precedence."""
        explicit_org = "explicit-org"
        extracted_org = "extracted-org"

        class MockGraphistry:
            def __init__(self):
                self._credentials = {"org_name": extracted_org}

            def api_token(self):
                return "fake-token"

        mock_g = MockGraphistry()

        with patch("graphistry.pygraphistry.GraphistryClient", return_value=mock_g):
            lui = louieai.louie(
                mock_g,
                org_name=explicit_org,  # This should win
                server_url="https://louie-dev.grph.xyz",
            )

            stored_org = lui._client._auth_manager._credentials.get("org_name")
            assert stored_org == explicit_org, (
                f"Expected explicit '{explicit_org}', got '{stored_org}'"
            )

    def test_env_var_beats_extraction(self):
        """Test that environment variable beats extraction."""
        env_org = "env-org"
        extracted_org = "extracted-org"

        class MockGraphistry:
            def __init__(self):
                self._credentials = {"org_name": extracted_org}

            def api_token(self):
                return "fake-token"

        mock_g = MockGraphistry()

        with (
            patch("graphistry.pygraphistry.GraphistryClient", return_value=mock_g),
            patch.dict(os.environ, {"GRAPHISTRY_ORG_NAME": env_org}),
        ):
            lui = louieai.louie(mock_g, server_url="https://louie-dev.grph.xyz")

            stored_org = lui._client._auth_manager._credentials.get("org_name")
            assert stored_org == env_org, (
                f"Expected env '{env_org}', got '{stored_org}'"
            )
