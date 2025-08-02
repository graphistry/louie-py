"""Notebook-friendly API for LouieAI.

This module provides a simplified interface optimized for Jupyter notebooks
and interactive data analysis.

Example:
    >>> import louieai as lui
    >>> lui("Show me sales data from last week")
    >>> df = lui.df  # Access the returned dataframe
    >>> lui("What are the top products?")
"""

from typing import TYPE_CHECKING

from .cursor import Cursor

if TYPE_CHECKING:
    # Type hints without circular imports
    from louieai._client import LouieClient  # noqa: F401

# Create singleton instance
_global_cursor: Cursor | None = None


def _get_cursor() -> Cursor:
    """Get or create the global cursor instance."""
    global _global_cursor
    if _global_cursor is None:
        _global_cursor = Cursor()
    return _global_cursor


# Create a callable proxy that delegates to the singleton
class _LuiProxy:
    """Proxy to make lui both callable and have properties."""

    def __call__(self, *args, **kwargs):
        return _get_cursor()(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(_get_cursor(), name)

    def __setattr__(self, name, value):
        setattr(_get_cursor(), name, value)

    def __getitem__(self, index):
        return _get_cursor()[index]

    def __repr__(self):
        return _get_cursor().__repr__()

    def _repr_html_(self):
        return _get_cursor()._repr_html_()

    @property
    def _cursor(self):
        """Access the underlying cursor for testing."""
        return _get_cursor()


# Export the cursor as 'lui' for the recommended usage pattern
lui = _LuiProxy()

# Also export for direct access if needed
__all__ = ["Cursor"]
