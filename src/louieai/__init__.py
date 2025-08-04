import sys
import types
from typing import Any

try:
    from ._version import __version__
except ImportError:
    # Fallback for development installs without setuptools_scm
    __version__ = "0.0.0+unknown"

from ._client import Response, Thread
from .notebook import Cursor


def _extract_org_name_from_graphistry(graphistry_client) -> str | None:
    """Extract org_name from existing PyGraphistry client.

    PyGraphistry clients can store org_name in several ways depending on version
    and authentication method. This function tries to extract it using a cascade
    approach.

    Args:
        graphistry_client: PyGraphistry client instance

    Returns:
        org_name if found, None otherwise
    """
    if not graphistry_client:
        return None

    # Method 1: Check if client has _credentials dict with org_name (most common)
    if (
        hasattr(graphistry_client, "_credentials")
        and graphistry_client._credentials
        and isinstance(graphistry_client._credentials, dict)
    ):
        org_name = graphistry_client._credentials.get("org_name")
        if org_name and not str(org_name).startswith("<MagicMock"):
            return str(org_name)

    # Method 2: Check if client has auth_manager with credentials
    if hasattr(graphistry_client, "_auth_manager") and graphistry_client._auth_manager:
        auth_mgr = graphistry_client._auth_manager
        if (
            hasattr(auth_mgr, "_credentials")
            and auth_mgr._credentials
            and isinstance(auth_mgr._credentials, dict)
        ):
            org_name = auth_mgr._credentials.get("org_name")
            if org_name and not str(org_name).startswith("<MagicMock"):
                return str(org_name)

    # Method 3: Check if client has _org_name attribute (fallback)
    if hasattr(graphistry_client, "_org_name") and graphistry_client._org_name:
        org_name = graphistry_client._org_name
        if org_name and not str(org_name).startswith("<MagicMock"):
            return str(org_name)

    # Method 4: Check if client has get_auth_info() method (newer versions)
    if hasattr(graphistry_client, "get_auth_info"):
        try:
            auth_info = graphistry_client.get_auth_info()
            if isinstance(auth_info, dict) and "org_name" in auth_info:
                org_name = auth_info["org_name"]
                if org_name and not str(org_name).startswith("<MagicMock"):
                    return str(org_name)
        except Exception:
            pass  # Ignore errors from get_auth_info

    # Method 5: Check if client has org_name() method
    if hasattr(graphistry_client, "org_name") and callable(graphistry_client.org_name):
        try:
            org_name = graphistry_client.org_name()
            if org_name and not str(org_name).startswith("<MagicMock"):
                return str(org_name)
        except Exception:
            pass  # Ignore errors from org_name()

    return None


def louie(
    graphistry_client: Any | None = None,
    share_mode: str = "Private",
    name: str | None = None,
    **kwargs: Any,
) -> Cursor:
    """Create a callable Louie interface.

    This factory function provides flexible ways to create a Louie client:

    1. Global client (uses environment variables):
       ```python
       lui = louie()
       lui("Hello, Louie!")
       ```

    2. From existing PyGraphistry client:
       ```python
       import graphistry
       gc = graphistry.client()
       gc.register(api=3, username="user", password="<password>")
       lui = louie(gc)
       lui("Analyze my data")
       ```

    3. With direct credentials:
       ```python
       lui = louie(username="user", password="<password>")
       lui = louie(personal_key_id="pk_123", personal_key_secret="sk_456")
       lui = louie(api_key="your_api_key")
       ```

    Args:
        graphistry_client: Optional PyGraphistry client or None for global
        share_mode: Default visibility mode - "Private", "Organization", or "Public"
        name: Optional thread name (auto-generated from first message if not provided)
        **kwargs: Authentication parameters passed to LouieClient
            - username: PyGraphistry username
            - password: PyGraphistry password
            - api_key: API key (alternative to username/password)
            - personal_key_id: Personal key ID for service accounts
            - personal_key_secret: Personal key secret
            - org_name: Organization name (optional)
            - server_url: Louie server URL (default: "https://den.louie.ai")
            - server: PyGraphistry server (default: from env or "hub.graphistry.com")
            - timeout: Overall timeout in seconds (default: 300s/5min)
            - streaming_timeout: Timeout for streaming chunks (default: 120s/2min)

    Returns:
        Cursor: A callable interface for natural language queries

    Examples:
        >>> # Using environment variables
        >>> lui = louie()
        >>> response = lui("What insights can you find?")
        >>> print(lui.text)

        >>> # With PyGraphistry client
        >>> import graphistry
        >>> g = graphistry.client()
        >>> g.register(api=3, username="alice", password="<password>")
        >>> lui = louie(g)
        >>> lui("Show me the patterns")

        >>> # Direct authentication with default visibility
        >>> lui = louie(
        ...     personal_key_id="pk_123",
        ...     personal_key_secret="sk_456",
        ...     org_name="my-org",
        ...     share_mode="Organization"  # All queries default to org visibility
        ... )
        >>> lui("Analyze fraud patterns")  # Shared within organization
        >>> lui("Private analysis", share_mode="Private")  # Override for this query

        >>> # Custom timeouts for long-running agentic flows
        >>> lui = louie(
        ...     username="alice",
        ...     password="<password>",
        ...     timeout=600,  # 10 minutes for complex analysis
        ...     streaming_timeout=180  # 3 minutes per chunk
        ... )
        >>> lui("Run comprehensive data analysis with multiple steps")
    """
    from ._client import LouieClient

    # If graphistry_client provided, create LouieClient with it
    if graphistry_client is not None:
        # Implement org_name cascade: explicit > env > extracted > None
        if "org_name" not in kwargs:
            # Check environment variable first
            import os

            env_org = os.environ.get("GRAPHISTRY_ORG_NAME")
            if env_org:
                kwargs["org_name"] = env_org
            else:
                # Extract from graphistry client as fallback
                extracted_org = _extract_org_name_from_graphistry(graphistry_client)
                if extracted_org:
                    kwargs["org_name"] = extracted_org

        client = LouieClient(graphistry_client=graphistry_client, **kwargs)
        return Cursor(client=client, share_mode=share_mode, name=name)

    # If kwargs provided, create LouieClient with them
    if kwargs:
        client = LouieClient(**kwargs)
        return Cursor(client=client, share_mode=share_mode, name=name)

    # Otherwise, create a new cursor with environment variables
    return Cursor(share_mode=share_mode, name=name)


__all__ = [
    "Cursor",
    "Response",
    "Thread",
    "__version__",
    "louie",
]


# Make the module itself callable
class CallableModule(types.ModuleType):
    """A module that can be called like a function."""

    def __init__(self, module):
        # Initialize the parent class first
        if module is not None and hasattr(module, "__name__"):
            super().__init__(module.__name__)
        else:
            super().__init__(__name__)

        # Then update the dictionary if possible
        if (
            module is not None
            and hasattr(module, "__dict__")
            and module.__dict__ is not None
        ):
            self.__dict__.update(module.__dict__)

    def __call__(self, *args, **kwargs):
        return louie(*args, **kwargs)


# Replace the module with a callable version
current_module = sys.modules.get(__name__)
if current_module is not None:
    sys.modules[__name__] = CallableModule(current_module)
