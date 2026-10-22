#!/usr/bin/env python3
"""Test org_name authentication flow to detect confused deputy problem."""

from unittest.mock import MagicMock, Mock, patch

import pytest

import louieai
from louieai._client import LouieClient
from louieai.auth import AuthManager

# The Graphistry server generates org slugs from the name typed when creating
# an org, and from the username for personal orgs. Expected values below are
# the server's output for each input; ``_to_slug`` must match it exactly.
SLUGIFY_PARITY_CASES = [
    # Already-generated slugs are left alone
    ("my_org", "my_org", "underscores are kept (#53)"),
    ("team_a-b", "team_a-b", "mixed _ and -"),
    ("example-org", "example-org", "plain slug"),
    ("alice1", "alice1", "personal slug with collision suffix"),
    ("a__b", "a__b", "inner underscore runs are kept"),
    # Display names
    ("My Org", "my-org", "spaces become -"),
    ("My Organization", "my-organization", "spaces become -"),
    ("UPPERCASE ORG", "uppercase-org", "lowercased"),
    ("My_Team Org", "my_team-org", "space to -, _ kept"),
    ("Test_Org-123", "test_org-123", "lowercased, _ kept"),
    ("Graphistry, Inc.", "graphistry-inc", "punctuation dropped"),
    ("Org with Special@#$%", "org-with-special", "symbols dropped"),
    ("rock&roll", "rockroll", "symbols dropped, not turned into -"),
    ("a - b", "a-b", "runs of space and - collapse"),
    ("  spaced  out  ", "spaced-out", "surrounding whitespace stripped"),
    ("my_org\n", "my_org", "trailing newline stripped"),
    ("--edge--", "edge", "leading/trailing - stripped"),
    ("_private_", "private", "leading/trailing _ stripped"),
    # Personal orgs: slug is generated from the username
    ("JohnDoe", "johndoe", "username case is lowered"),
    ("John.Doe", "johndoe", "dots dropped, not turned into -"),
    ("john.doe@example.com", "johndoeexamplecom", "email-style username"),
    ("a+b", "ab", "+ dropped"),
    # Non-ASCII: transliterated where possible; header values must be ASCII
    ("café", "cafe", "accents transliterated"),
    ("Ünïcödé Örg", "unicode-org", "accents transliterated"),
    ("\uff21\uff43\uff4d\uff45", "acme", "fullwidth letters normalized"),
    ("foo\u2014bar", "foobar", "em dash dropped"),
    ("ø", "", "no ASCII form: dropped"),
    ("日本", "", "no ASCII form: dropped"),
]


class TestOrgAuthFlow:
    """Test organization authentication flow."""

    def test_direct_client_org_name_flow(self):
        """Test that LouieClient correctly handles org_name parameter."""
        target_org = "example-org"

        # Mock PyGraphistry client
        mock_graphistry = MagicMock()
        mock_graphistry.api_token.return_value = "fake-jwt-token-123"

        with patch("louieai.auth.GraphistryClient", return_value=mock_graphistry):
            client = LouieClient(
                personal_key_id="test-personal-key-id",
                personal_key_secret="test-personal-key-secret",
                org_name=target_org,
                graphistry_server="graphistry.example.com",
                server_url="https://louie.example.com",
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
        target_org = "example-org"

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
            server_url="https://louie.example.com",
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
        test_cases = [(raw, slug) for raw, slug, _why in SLUGIFY_PARITY_CASES]
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

            # Simulate: g = graphistry.register(org_name='example-org', ...)
            g = mock_registered_client

            # Step 2: User creates LouieAI interface with the registered client
            lui = louieai.louie(
                g, server_url="https://louie.example.com", share_mode="Private"
            )

            # Step 3: User makes a query - this should use the correct org
            # But due to confused deputy problem, it might not

            # Check what org context the LouieAI client will use
            auth_manager = lui._client._auth_manager
            stored_org = auth_manager._credentials.get("org_name")

            # This should be 'example-org' but is likely None
            assert stored_org == "example-org", (
                f"Confused deputy: Expected 'example-org', got '{stored_org}'"
            )

            # Check headers that would be sent to LouieAI API
            headers = lui._client._get_headers()
            assert "X-Graphistry-Org" in headers, (
                "Missing org header - API calls will be made as 'personal'"
            )

            assert headers["X-Graphistry-Org"] == "example-org", (
                f"Wrong org in API headers: {headers.get('X-Graphistry-Org')}"
            )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(raw, slug) for raw, slug, _why in SLUGIFY_PARITY_CASES],
    ids=[why for _raw, _slug, why in SLUGIFY_PARITY_CASES],
)
def test_to_slug_matches_server_slugify(raw, expected):
    assert LouieClient._to_slug(raw) == expected


@pytest.mark.parametrize("raw", [raw for raw, _slug, _why in SLUGIFY_PARITY_CASES])
def test_to_slug_is_idempotent(raw):
    """Slugs the server generated must pass through unchanged."""
    once = LouieClient._to_slug(raw)
    assert LouieClient._to_slug(once) == once


# "SITE" is the slug the server gives its site-wide org; "Acme_Corp" stands in
# for a slug an admin set directly. Neither is slugify() output, so
# converting them would name a different org.
@pytest.mark.parametrize("slug", ["my_org", "team_a-b", "SITE", "Acme_Corp"])
def test_graphistry_client_slug_reaches_header_unchanged(slug, monkeypatch):
    """#53: the default ``louie(graphistry_client=g)`` flow sends g's slug as-is."""
    import graphistry

    monkeypatch.delenv("GRAPHISTRY_ORG_NAME", raising=False)
    g = graphistry.client()
    g.session.org_name = slug
    g.session.api_token = "fake-token"

    lui = louieai.louie(graphistry_client=g, server_url="https://test.louie.ai")

    assert lui._client._get_headers()["X-Graphistry-Org"] == slug


def test_explicit_org_name_confirmed_by_graphistry_is_sent_as_is(monkeypatch):
    """An explicit org_name equal to g's active slug is a real slug: no rewrite."""
    import graphistry

    monkeypatch.delenv("GRAPHISTRY_ORG_NAME", raising=False)
    g = graphistry.client()
    g.session.org_name = "SITE"
    g.session.api_token = "fake-token"

    lui = louieai.louie(
        graphistry_client=g, org_name="SITE", server_url="https://test.louie.ai"
    )

    assert lui._client._get_headers()["X-Graphistry-Org"] == "SITE"


def test_padded_confirmed_org_name_is_sent_trimmed(monkeypatch):
    """A trailing newline (e.g. from an env file) must not turn SITE into site."""
    import graphistry

    monkeypatch.delenv("GRAPHISTRY_ORG_NAME", raising=False)
    g = graphistry.client()
    g.session.org_name = "SITE"
    g.session.api_token = "fake-token"

    lui = louieai.louie(
        graphistry_client=g, org_name=" SITE\n", server_url="https://test.louie.ai"
    )

    assert lui._client._get_headers()["X-Graphistry-Org"] == "SITE"


@pytest.mark.parametrize(
    ("org_name", "active_slug", "expected"),
    [
        # A different value than g's active org: convert like the server would
        ("My Org", "my-org", "my-org"),
        ("JohnDoe", "other", "johndoe"),
        # Unconfirmed values are always converted, even if they look like slugs
        ("SITE", None, "site"),
        # A non-ASCII active slug can't be sent in a header; don't send it
        ("café", "café", "cafe"),
    ],
)
def test_unconfirmed_org_name_is_converted(org_name, active_slug, expected):
    mock_graphistry = MagicMock()
    mock_graphistry.api_token.return_value = "fake-token"
    mock_graphistry.org_name.return_value = active_slug

    with patch("louieai.auth.GraphistryClient", return_value=mock_graphistry):
        client = LouieClient(
            personal_key_id="test_key",
            personal_key_secret="test_secret",
            org_name=org_name,
            server_url="https://test.louie.ai",
        )
        assert client._get_headers()["X-Graphistry-Org"] == expected


def test_org_name_lookup_failure_falls_back_to_conversion():
    mock_graphistry = MagicMock()
    mock_graphistry.api_token.return_value = "fake-token"
    mock_graphistry.org_name.side_effect = RuntimeError("no session")

    with patch("louieai.auth.GraphistryClient", return_value=mock_graphistry):
        client = LouieClient(
            personal_key_id="test_key",
            personal_key_secret="test_secret",
            org_name="My Org",
            server_url="https://test.louie.ai",
        )
        assert client._get_headers()["X-Graphistry-Org"] == "my-org"


@pytest.mark.parametrize("org_name", ["my_org", "John.Doe", "café", "My Org", "日本"])
def test_org_header_is_sendable(org_name):
    """The header must survive a real httpx request (non-ASCII values can't)."""
    import httpx

    seen = {}

    def handler(request):
        seen["org"] = request.headers.get("X-Graphistry-Org")
        return httpx.Response(200, json={})

    client = LouieClient(
        token="fake-token", org_name=org_name, server_url="https://test.louie.ai"
    )
    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        http.get("https://test.louie.ai/api/x", headers=client._get_headers())
    assert seen["org"] == client._to_slug(org_name)
