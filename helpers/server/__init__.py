# helpers/server/__init__.py
"""helpers.server

Small, local-only server utilities (no framework dependency).
"""

from .static_file_server import StaticFileServer

__all__ = ["StaticFileServer"]
