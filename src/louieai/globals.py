"""Module providing a global singleton cursor for convenient notebook usage.

This module provides a pre-configured global cursor instance that uses
environment variables for authentication.

Example:
    >>> from louieai.globals import lui
    >>> lui("What insights can you find in my data?")
    >>> print(lui.text)
    >>> df = lui.df
"""

from .notebook import lui

__all__ = ["lui"]
