"""Backend implementations for text injection."""

from .xdotool_backend import XdotoolBackend
from .portal_backend import PortalBackend
from .ydotool_backend import YdotoolBackend

__all__ = ["XdotoolBackend", "PortalBackend", "YdotoolBackend"]
