# tests/test_zones_serde_templates.py

from __future__ import annotations

import json
from pathlib import Path

import pytest

from helpers.zones.serde import (
    dumps_zones_library,
    loads_zones_library,
    zones_template_path,
)


def test_zones_serde_roundtrip() -> None:
    doc = {
        "schema_version": 1,
        "presets": {
            "default": {
                "meta": {"name": "Default Preset", "tags": []},
                "zones": {
                    "zone_1": {
                        "enabled": True,
                        "intent": "generic",
                        "geometry": {"type": "rect_norm", "xyxy": [0.1, 0.1, 0.4, 0.4]},
                        "tags": [],
                        "style": {},
                        "consumers": {},
                    }
                },
            }
        },
    }

    s = dumps_zones_library(doc, indent=2)
    out = loads_zones_library(s)
    assert out["schema_version"] == 1
    assert "default" in out["presets"]
    assert "zone_1" in out["presets"]["default"]["zones"]


def test_zones_template_path_convention(tmp_path: Path) -> None:
    # Emulate helpers root with templates/zones/...
    helpers_root = tmp_path / "helpers"
    tpl_dir = helpers_root / "templates" / "zones"
    tpl_dir.mkdir(parents=True)

    p = zones_template_path("library.json", helpers_root=helpers_root)
    assert p == tpl_dir / "library.json"
