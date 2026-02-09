# helpers/zones/serde.py
from __future__ import annotations

"""
helpers.zones.serde
-------------------

JSON load/save utilities for the Zones Preset Library document.

Design goals:
- Dependency-light: stdlib json + helpers.zones.schema
- Frontend-agnostic
- Optional integration with helpers.catalogloader (if present), but not required

Conventions:
- Templates live under: helpers/templates/zones/
- Typical files: library.json, preset.json, zone.json
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .schema import ensure_library_shape


def loads_zones_library(text: str) -> Dict[str, Any]:
    doc = json.loads(text)
    ensure_library_shape(doc)
    return doc


def dumps_zones_library(doc: Dict[str, Any], *, indent: int = 2, sort_keys: bool = True) -> str:
    ensure_library_shape(doc)
    return json.dumps(doc, indent=indent, sort_keys=sort_keys, ensure_ascii=False)


def load_zones_library(path: Path, *, encoding: str = "utf-8") -> Dict[str, Any]:
    text = path.read_text(encoding=encoding)
    return loads_zones_library(text)


def save_zones_library(
    path: Path,
    doc: Dict[str, Any],
    *,
    encoding: str = "utf-8",
    indent: int = 2,
) -> None:
    text = dumps_zones_library(doc, indent=indent)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding=encoding)


# ─────────────────────────────────────────────────────────────
# Optional: template/config conventions via helpers/catalogloader
# ─────────────────────────────────────────────────────────────

def _helpers_root_from_here() -> Path:
    """
    Resolve the helpers/ root based on this file location.

    Expected path:
      helpers/zones/serde.py  -> parents[1] == helpers/
    """
    return Path(__file__).resolve().parents[1]


def zones_template_path(name: str, *, helpers_root: Optional[Path] = None) -> Path:
    """
    Resolve a zones template path under:
      helpers/templates/zones/<name>
    """
    root = (helpers_root or _helpers_root_from_here()).resolve()
    return root / "templates" / "zones" / name


def load_zones_template(name: str = "library.json", *, helpers_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load and validate a zones template.

    This does NOT require CatalogLoader, but follows the same path convention.
    """
    path = zones_template_path(name, helpers_root=helpers_root)
    return load_zones_library(path)


def try_load_zones_template_via_catalogloader(
    name: str = "library.json",
    *,
    helpers_root: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """
    If helpers.catalogloader is available, load template using that mechanism.
    Otherwise return None.

    This keeps zones.serde usable even when the catalogloader package isn't included
    in a minimal deployment.
    """
    try:
        from helpers.catalogloader import CatalogLoader  # type: ignore
    except Exception:
        return None

    # Zones schema validator returns dict (validated shape)
    def _validate(raw: Any) -> Dict[str, Any]:
        return ensure_library_shape(raw)

    def _dump(doc: Dict[str, Any]) -> Dict[str, Any]:
        ensure_library_shape(doc)
        return doc

    loader = CatalogLoader(
        app_name="zones",
        validate=_validate,
        dump=_dump,
        schema_name="zones_library",
        schema_version=1,
        helpers_root=helpers_root,
    )
    # Uses helpers/templates/zones/<name>
    cat = loader.load_template_catalog(name)
    return cat.dump(_dump)
