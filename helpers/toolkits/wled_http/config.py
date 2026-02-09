# helpers/toolkits/wled_http/config.py
from __future__ import annotations

"""
helpers.toolkits.wled_http.config
---------------------------------

Default config loader for the WLED HTTP toolkit.

Convention:
- Default config lives at: helpers/configs/wled_http/default.json

This module is intentionally small and dependency-light.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from helpers.validation import (
    ValidationError,
    ensure_dict,
    ensure_float,
    ensure_int,
    ensure_ip,
)


def _helpers_root_from_here() -> Path:
    """
    Resolve the helpers/ root based on this file location.

    Expected path:
      helpers/toolkits/wled_http/config.py
      parents:
        [0]=config.py
        [1]=wled_http
        [2]=toolkits
        [3]=helpers   <-- we want this
    """
    return Path(__file__).resolve().parents[3]


def default_config_path(*, helpers_root: Optional[Path] = None) -> Path:
    root = (helpers_root or _helpers_root_from_here()).resolve()
    return root / "configs" / "wled_http" / "default.json"


@dataclass(frozen=True)
class WledHttpConfig:
    ip: str
    http_port: int = 80
    timeout_s: float = 2.0

    @staticmethod
    def from_dict(d: Dict[str, Any], *, path: str = "wled_http") -> "WledHttpConfig":
        obj = ensure_dict(d, path=path)

        ip = ensure_ip(obj.get("ip"), path=f"{path}.ip")
        http_port = ensure_int(obj.get("http_port", 80), path=f"{path}.http_port", min_v=1, max_v=65535)
        timeout_s = ensure_float(obj.get("timeout_s", 2.0), path=f"{path}.timeout_s", min_v=0.1, max_v=60.0)

        return WledHttpConfig(ip=ip, http_port=http_port, timeout_s=timeout_s)


def load_default_config(*, helpers_root: Optional[Path] = None) -> WledHttpConfig:
    p = default_config_path(helpers_root=helpers_root)
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValidationError(f"Failed to load WLED config JSON: {p}") from e

    return WledHttpConfig.from_dict(raw, path="wled_http")
