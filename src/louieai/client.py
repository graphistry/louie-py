from typing import Any

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
        token: str | None = graphistry.api_token()
        if token is None:
            raise RuntimeError(
                "No Graphistry API token found. Please call "
                "graphistry.register() to authenticate."
            )
        # Prepare the request
        headers = {"Authorization": f"Bearer {token}"}
        # TODO: confirm correct Louie endpoint and response format when official
        # docs are available
        url = f"{self.server_url}/api/ask"
        try:
            response = httpx.post(
                url, json={"prompt": prompt}, headers=headers, timeout=30.0
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Include response text or json in error
            error_text = ""
            try:
                error_data = response.json()
                error_text = error_data.get("error", "") or error_data.get(
                    "message", ""
                )
            except Exception:
                error_text = response.text
            raise RuntimeError(
                f"LouieAI API returned error {response.status_code}: {error_text}"
            ) from e
        except httpx.RequestError as e:
            # Network or other request issue
            raise RuntimeError(f"Failed to connect to LouieAI: {e}") from e
        # Assuming the API returns JSON
        return response.json()
