# services/vision/catalog_seed.py
# Reads the default JSON seeds from helpers/configs/...

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_json_file(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at {path}, got {type(data).__name__}")
    return data


def seed_layer_catalog_from_repo(repo_root: Path) -> Dict[str, Any]:
    return load_json_file(repo_root / "helpers" / "configs" / "layers" / "default.json")


def seed_annotation_catalog_from_repo(repo_root: Path) -> Dict[str, Any]:
    return load_json_file(repo_root / "helpers" / "configs" / "vision" / "annotations" / "default.json")
