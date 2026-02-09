# tests/test_server_static_file_server.py

from __future__ import annotations

import time
from pathlib import Path

from helpers.server.static_file_server import StaticFileServer


def test_static_file_server_start_stop(tmp_path: Path) -> None:
    # Create a small directory to serve
    root = tmp_path / "www"
    root.mkdir()
    (root / "index.html").write_text("<h1>ok</h1>", encoding="utf-8")

    # Port 0 lets OS select a free port (works with TCPServer)
    srv = StaticFileServer(root_dir=root, host="127.0.0.1", port=0, daemon=True)

    srv.start()
    # Give the thread a moment to spin up
    time.sleep(0.05)

    # No direct URL assertions needed: this is a lifecycle smoke test.
    srv.stop()
