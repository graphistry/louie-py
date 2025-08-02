try:
    from ._version import __version__
except ImportError:
    # Fallback for development installs without setuptools_scm
    __version__ = "0.0.0+unknown"

from typing import Any

from ._client import Response, Thread
from .notebook import Cursor


def louie(
    graphistry_client: Any | None = None,
    **kwargs: Any
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
       gc.register(api=3, username="user", password="pass")
       lui = louie(gc)
       lui("Analyze my data")
       ```

    3. With direct credentials:
       ```python
       lui = louie(username="user", password="pass")
       lui = louie(personal_key_id="pk_123", personal_key_secret="sk_456")
       lui = louie(api_key="your_api_key")
       ```

    Args:
        graphistry_client: Optional PyGraphistry client or None for global
        **kwargs: Authentication parameters passed to LouieClient
            - username: PyGraphistry username
            - password: PyGraphistry password
            - api_key: API key (alternative to username/password)
            - personal_key_id: Personal key ID for service accounts
            - personal_key_secret: Personal key secret
            - org_name: Organization name (optional)
            - server_url: Louie server URL (default: "https://den.louie.ai")
            - server: PyGraphistry server (default: from env or "hub.graphistry.com")

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
        >>> g.register(api=3, username="alice", password="pass")
        >>> lui = louie(g)
        >>> lui("Show me the patterns")

        >>> # Direct authentication
        >>> lui = louie(
        ...     personal_key_id="pk_123",
        ...     personal_key_secret="sk_456",
        ...     org_name="my-org"
        ... )
        >>> lui("Analyze fraud patterns")
    """
    from ._client import LouieClient

    # If graphistry_client provided, create LouieClient with it
    if graphistry_client is not None:
        client = LouieClient(graphistry_client=graphistry_client, **kwargs)
        return Cursor(client=client)

    # If kwargs provided, create LouieClient with them
    if kwargs:
        client = LouieClient(**kwargs)
        return Cursor(client=client)

    # Otherwise, create a new cursor with environment variables
    return Cursor()


__all__ = [
    "Cursor",
    "Response",
    "Thread",
    "__version__",
    "louie",
]
