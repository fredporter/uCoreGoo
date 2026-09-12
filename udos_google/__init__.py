"""udos-google package."""

from .src.contracts import GoogleBridgeContract, default_google_contract
from .src.routes import GoogleBridgeRoutes, register_routes
from .src.service import GoogleBridgeService


def setup(_app=None):
    """Plugin setup hook for uCore extension loader."""
    return None


__all__ = [
    "GoogleBridgeContract",
    "GoogleBridgeRoutes",
    "GoogleBridgeService",
    "default_google_contract",
    "register_routes",
    "setup",
]
