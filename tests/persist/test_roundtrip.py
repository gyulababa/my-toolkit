# tests/persist/test_roundtrip.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from helpers.catalog import EditableCatalog
from helpers.persist import CatalogLoader, PersistedCatalogLoader


def test_persist_roundtrip_load_active_editable(tmp_path: Path) -> None:
    persist_root = tmp_path / "persist"

    def _validate(raw: Any) -> Dict[str, Any]:
        return raw  # simple identity validator for test

    def _dump(doc: Dict[str, Any]) -> Dict[str, Any]:
        return doc  # simple identity dumper for test

    loader = CatalogLoader(
        app_name="demo",
        validate=_validate,
        dump=_dump,
        schema_name="demo_schema",
        schema_version=1,
        helpers_root=tmp_path / "helpers",
    )
    persisted = PersistedCatalogLoader(loader=loader, domain="demo")

    original = EditableCatalog(raw={"alpha": 1, "beta": [1, 2, 3]}, schema_name="demo_schema", schema_version=1)
    persisted.save_new_revision(persist_root, original, note="seed", make_active=True)

    loaded = persisted.load_active_editable(persist_root)
    assert loaded.raw == original.raw
