try:
    from ._version import __version__
except ImportError:
    # Fallback for development installs without setuptools_scm
    __version__ = "0.0.0+unknown"

from .client import LouieClient

__all__ = ["LouieClient", "__version__"]
