"""Routes entrypoint for udos-google plugin."""

from .src.routes import (
    GoogleBridgeRoutes,
    get_routes,
    register_routes,
)

__all__ = ["GoogleBridgeRoutes", "get_routes", "register_routes"]
