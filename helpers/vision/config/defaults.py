# helpers/vision/config/defaults.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

from helpers.catalogloader import CatalogLoader
from helpers.catalog import Catalog, EditableCatalog

from .schema import VisionConfig, ensure_vision_config
from .dump import dump_vision_config


def vision_catalog_loader(*, helpers_root: Optional[Path] = None) -> CatalogLoader[VisionConfig]:
    return CatalogLoader(
        app_name="vision",
        validate=ensure_vision_config,
        dump=dump_vision_config,
        schema_name="vision_config",
        schema_version=1,
        helpers_root=helpers_root,
    )


def load_default_config_catalog(*, helpers_root: Optional[Path] = None) -> Catalog[VisionConfig]:
    loader = vision_catalog_loader(helpers_root=helpers_root)
    return loader.load_config_catalog("default.json")


def load_default_config_editable(*, helpers_root: Optional[Path] = None, history=None) -> EditableCatalog[VisionConfig]:
    loader = vision_catalog_loader(helpers_root=helpers_root)
    return loader.load_config_editable("default.json", history=history)


def load_template_catalog(name: str, *, helpers_root: Optional[Path] = None) -> Catalog[VisionConfig]:
    loader = vision_catalog_loader(helpers_root=helpers_root)
    return loader.load_template_catalog(name)


def load_template_editable(name: str, *, helpers_root: Optional[Path] = None, history=None) -> EditableCatalog[VisionConfig]:
    loader = vision_catalog_loader(helpers_root=helpers_root)
    return loader.load_template_editable(name, history=history)
