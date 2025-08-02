"""Custom exceptions for notebook-friendly API with helpful messages."""


class NotebookError(Exception):
    """Base exception for notebook API errors."""

    def __init__(self, message: str, suggestion: str | None = None):
        """Initialize with message and optional suggestion.

        Args:
            message: The error message
            suggestion: Optional suggestion for fixing the error
        """
        self.message = message
        self.suggestion = suggestion

        # Build full message
        full_message = message
        if suggestion:
            full_message = f"{message}\n💡 Try: {suggestion}"

        super().__init__(full_message)


class NoDataFrameError(NotebookError):
    """Raised when no dataframe is available in response."""

    def __init__(self):
        super().__init__(
            "No dataframe in the latest response.",
            "lui('show the data as a table') or lui('convert to dataframe')",
        )


class NoResponseError(NotebookError):
    """Raised when trying to access data before any queries."""

    def __init__(self):
        super().__init__(
            "No responses yet. Make a query first.", "lui('your question here')"
        )


class SessionExpiredError(NotebookError):
    """Raised when session has expired."""

    def __init__(self):
        super().__init__(
            "Session expired. Starting a new conversation.",
            "Continue with your query - a new session will be created automatically.",
        )


class AuthenticationError(NotebookError):
    """Raised when authentication fails."""

    def __init__(self):
        super().__init__(
            "Authentication failed. Check your credentials.",
            "Set GRAPHISTRY_USERNAME and GRAPHISTRY_PASSWORD environment variables, "
            "or pass credentials to LouieClient.",
        )


class ConnectionError(NotebookError):
    """Raised when connection to server fails."""

    def __init__(self, server: str):
        super().__init__(
            f"Could not connect to server: {server}",
            "Check your internet connection and server URL. "
            "Default server is 'louie.ai'.",
        )
