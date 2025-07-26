from typing import Any, Optional

import graphistry
import httpx


class LouieClient:
    """
    A client for interacting with the Louie.ai service.
    Uses Graphistry's authentication token for authorization.
    """
    def __init__(self, server_url: str = "https://den.louie.ai"):
        """
        Initialize the LouieClient.

        :param server_url: Base URL for the Louie.ai service
                          (default is the production Louie endpoint).
        """
        self.server_url = server_url
        # Ensure Graphistry is registered (i.e., an API token is available)
        # We don't fetch the token here to avoid doing it at import;
        # will do when needed.

    def ask(self, prompt: str) -> Any:
        """
        Send a prompt to Louie.ai and get a response.

        :param prompt: The prompt or query to send to the Louie.ai service.
        :return: The response from Louie.ai (parsed from JSON),
                 or raises an exception on error.
        """
        # Get the current Graphistry API token for auth
        token: Optional[str] = graphistry.api_token()
        if token is None:
            raise RuntimeError(
                "No Graphistry API token found. Please call "
                "graphistry.register() to authenticate."
            )
        # Prepare the request
        headers = {"Authorization": f"Bearer {token}"}
        # Assuming an endpoint; this may change when actual API is known
        url = f"{self.server_url}/api/ask"
        try:
            response = httpx.post(
                url, json={"prompt": prompt}, headers=headers, timeout=30.0
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            # For now, raise an error if request fails
            raise RuntimeError(f"Request to Louie.ai failed: {e}") from e
        # Assuming the API returns JSON
        return response.json()
