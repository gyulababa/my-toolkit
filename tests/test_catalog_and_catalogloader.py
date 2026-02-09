# tests/test_catalog_and_catalogloader.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from helpers.catalog import Catalog, EditableCatalog
from helpers.catalogloader.loader import CatalogLoader
from helpers.validation import ValidationError


def _validate_doc(raw: Any) -> Dict[str, Any]:
    # Minimal schema: must be dict and must contain schema_version == 1
    if not isinstance(raw, dict):
        raise ValidationError("doc must be dict")
    if raw.get("schema_version") != 1:
        raise ValidationError("schema_version must be 1")
    return raw


def _dump_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    # For dict-based docs this is identity, but keep the hook explicit.
    if not isinstance(doc, dict):
        raise TypeError("doc must be dict")
    return dict(doc)


def test_catalog_load_and_dump_roundtrip() -> None:
    raw = {"schema_version": 1, "items": {"a": 1}}
    cat = Catalog.load(raw, validate=_validate_doc, schema_name="test", schema_version=1)
    dumped = cat.dump(_dump_doc)
    assert dumped == raw


def test_editable_catalog_validate_and_to_catalog() -> None:
    editable = EditableCatalog(raw={"schema_version": 1, "items": {}}, schema_name="test", schema_version=1)
    typed = editable.validate(_validate_doc)
    assert typed["schema_version"] == 1

    cat = editable.to_catalog(validate=_validate_doc)
    assert isinstance(cat, Catalog)
    assert cat.doc["schema_version"] == 1


def test_catalogloader_template_and_config_paths(tmp_path: Path) -> None:
    # Build a fake helpers root:
    #   <root>/templates/myapp/x.json
    #   <root>/configs/myapp/default.json
    root = tmp_path / "helpers_root"
    (root / "templates" / "myapp").mkdir(parents=True)
    (root / "configs" / "myapp").mkdir(parents=True)

    tpl_path = root / "templates" / "myapp" / "x.json"
    cfg_path = root / "configs" / "myapp" / "default.json"

    tpl_path.write_text(json.dumps({"schema_version": 1, "items": {"tpl": True}}), encoding="utf-8")
    cfg_path.write_text(json.dumps({"schema_version": 1, "items": {"cfg": True}}), encoding="utf-8")

    loader = CatalogLoader(
        app_name="myapp",
        validate=_validate_doc,
        dump=_dump_doc,
        schema_name="myapp_catalog",
        schema_version=1,
        helpers_root=root,
    )

    assert loader.template_path("x.json") == tpl_path
    assert loader.config_path("default.json") == cfg_path

    tpl_cat = loader.load_template_catalog("x.json")
    assert tpl_cat.doc["items"]["tpl"] is True

    cfg_cat = loader.load_config_catalog("default.json")
    assert cfg_cat.doc["items"]["cfg"] is True


def test_catalogloader_save_editable_validates(tmp_path: Path) -> None:
    root = tmp_path / "helpers_root"
    (root / "templates" / "myapp").mkdir(parents=True)
    (root / "configs" / "myapp").mkdir(parents=True)

    loader = CatalogLoader(
        app_name="myapp",
        validate=_validate_doc,
        dump=_dump_doc,
        schema_name="myapp_catalog",
        schema_version=1,
        helpers_root=root,
    )

    out_path = tmp_path / "out.json"
    editable = EditableCatalog(raw={"schema_version": 1, "items": {"ok": 1}})

    loader.save_editable(out_path, editable, validate_before_save=True)
    assert out_path.exists()

    # Invalid should raise
    bad = EditableCatalog(raw={"schema_version": 2})
    with pytest.raises(ValidationError):
        loader.save_editable(out_path, bad, validate_before_save=True)
