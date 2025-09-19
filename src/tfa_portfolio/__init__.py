"""Top-level package for the TFA Portfolio automation toolkit."""

from importlib import metadata

try:
    __version__ = metadata.version("tfa-portfolio")
except metadata.PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0"

__all__ = ["__version__"]
