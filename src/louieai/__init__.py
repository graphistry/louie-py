try:
    from ._version import __version__
except ImportError:
    # Fallback for development installs without setuptools_scm
    __version__ = "0.0.0+unknown"

from .auth import AuthManager
from .client import LouieClient, Response, Thread

__all__ = ["AuthManager", "LouieClient", "Response", "Thread", "__version__"]
