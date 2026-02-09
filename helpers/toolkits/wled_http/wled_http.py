# helpers/toolkits/wled_http/wled_http.py
from __future__ import annotations

"""
helpers.toolkits.wled_http.wled_http
------------------------------------

Minimal HTTP client for WLED JSON state.

WLED endpoints:
- GET  /json/state  -> returns full current state JSON
- POST /json/state  -> applies a JSON patch / state update

This client stays intentionally tiny and UI-agnostic.

Config defaults:
- If you want a conventional default config, use:
    WledHttpClient.from_default_config()

Default config location:
  helpers/configs/wled_http/default.json
"""

import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .config import WledHttpConfig, load_default_config


class WledHttpClient:
    def __init__(self, ip: str, http_port: int = 80, timeout_s: float = 2.0) -> None:
        self._base = f"http://{ip}:{int(http_port)}"
        self._timeout = float(timeout_s)

    @classmethod
    def from_config(cls, cfg: WledHttpConfig) -> "WledHttpClient":
        return cls(ip=cfg.ip, http_port=cfg.http_port, timeout_s=cfg.timeout_s)

    @classmethod
    def from_default_config(cls, *, helpers_root: Optional[Path] = None) -> "WledHttpClient":
        """
        Create a client using helpers/configs/wled_http/default.json
        """
        cfg = load_default_config(helpers_root=helpers_root)
        return cls.from_config(cfg)

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self._base}{path}"

    def get_state(self) -> Dict[str, Any]:
        """Fetch current WLED state JSON."""
        url = self._url("/json/state")
        with urllib.request.urlopen(url, timeout=self._timeout) as resp:
            data = resp.read()
        return json.loads(data.decode("utf-8"))

    def set_state(self, state_patch: Dict[str, Any]) -> None:
        """Apply a state patch via POST /json/state."""
        url = self._url("/json/state")
        payload = json.dumps(state_patch).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self._timeout) as resp:
            resp.read()
