# tests/test_catalogloader_deprecation.py
from __future__ import annotations

import importlib
import sys
import warnings
from pathlib import Path
from typing import Any, Dict


def _purge_catalogloader_modules() -> None:
    for name in list(sys.modules):
        if name == "helpers.catalogloader" or name.startswith("helpers.catalogloader."):
            del sys.modules[name]


def _has_deprecation_warning(records: list[warnings.WarningMessage], *, needle: str) -> bool:
    for record in records:
        if issubclass(record.category, DeprecationWarning) and needle in str(record.message):
            return True
    return False


def test_catalogloader_import_warns() -> None:
    _purge_catalogloader_modules()
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always", DeprecationWarning)
        import helpers.catalogloader as catalogloader  # noqa: F401
    assert _has_deprecation_warning(records, needle="helpers.catalogloader is deprecated")


def test_catalogloader_loader_import_warns() -> None:
    _purge_catalogloader_modules()
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always", DeprecationWarning)
        importlib.import_module("helpers.catalogloader.loader")
    assert _has_deprecation_warning(records, needle="helpers.catalogloader.loader is deprecated")


def test_catalogloader_construct_warns() -> None:
    _purge_catalogloader_modules()
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always", DeprecationWarning)
        from helpers.catalogloader import CatalogLoader

        def _validate(raw: Any) -> Dict[str, Any]:
            return raw  # pragma: no cover - trivial fixture

        def _dump(doc: Dict[str, Any]) -> Dict[str, Any]:
            return doc  # pragma: no cover - trivial fixture

        _ = CatalogLoader(app_name="zones", validate=_validate, dump=_dump, helpers_root=Path.cwd())
    assert _has_deprecation_warning(records, needle="helpers.catalogloader is deprecated")
