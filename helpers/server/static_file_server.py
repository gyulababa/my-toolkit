# helpers/server/static_file_server.py
from __future__ import annotations

import contextlib
import http.server
import socketserver
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class _ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


@dataclass
class StaticFileServer:
    """
    Minimal local HTTP static file server.

    - Serves a directory over HTTP
    - Runs in a background thread
    - Provides start()/stop() lifecycle

    Intended for:
    - previewing exported artifacts
    - serving dashboard assets
    - quick local debugging
    """
    root_dir: Path
    host: str = "127.0.0.1"
    port: int = 8000
    daemon: bool = True

    _httpd: Optional[_ThreadedTCPServer] = None
    _thread: Optional[threading.Thread] = None

    def start(self) -> None:
        root = Path(self.root_dir).expanduser().resolve()
        if not root.exists():
            raise FileNotFoundError(str(root))

        # Prefer directory= parameter (py3.7+)
        handler_cls = http.server.SimpleHTTPRequestHandler
        try:
            def _handler(*args, **kwargs):
                return http.server.SimpleHTTPRequestHandler(*args, directory=str(root), **kwargs)
            handler = _handler  # type: ignore
        except TypeError:
            import os
            os.chdir(str(root))
            handler = handler_cls  # type: ignore

        self._httpd = _ThreadedTCPServer((self.host, int(self.port)), handler)

        def _serve() -> None:
            assert self._httpd is not None
            with contextlib.suppress(Exception):
                self._httpd.serve_forever(poll_interval=0.25)

        self._thread = threading.Thread(
            target=_serve,
            name=f"static-http-{self.host}:{self.port}",
            daemon=self.daemon,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._httpd is not None:
            with contextlib.suppress(Exception):
                self._httpd.shutdown()
            with contextlib.suppress(Exception):
                self._httpd.server_close()
        self._httpd = None
        self._thread = None
