# services/vision/layers_service.py

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from helpers.persist import CatalogLoader
from helpers.catalog import EditableCatalog

from services.domain.base_domain_service import BaseDomainService
from services.vision.persist_impl import PersistedCatalogLoader

from helpers.vision.overlays.validators import validate_layer_catalog, dump_identity


class LayersService(BaseDomainService):
    """
    Domain: layers
    Seed: helpers/configs/layers/default.json  (app_name="layers")
    """

    def __init__(self, *, persist_root: Path, history=None, helpers_root: Optional[Path] = None):
        loader = CatalogLoader[Dict[str, Any]](
            app_name="layers",
            validate=validate_layer_catalog,
            dump=dump_identity,
            schema_name="vision.layer_catalog",
            schema_version=1,
            helpers_root=helpers_root,
        )

        persisted = PersistedCatalogLoader[Dict[str, Any]](
            loader=loader,
            domain="layers",
            seed_raw=lambda: loader.load_raw(loader.config_path("default.json")),
        )

        super().__init__(persisted=persisted, history=history)
        self.persist_root = persist_root

    def load_active_raw(self) -> Dict[str, Any]:
        return self.persisted.load_active_raw(self.persist_root)

    def load_active_editable(self) -> EditableCatalog[Dict[str, Any]]:
        return self.persisted.load_active_editable(self.persist_root, history=self.history)

    def save_new_raw(self, raw: Dict[str, Any], *, note: Optional[str] = None, make_active: bool = True) -> Path:
        editable = EditableCatalog(raw=raw, schema_name=self.persisted.loader.schema_name, schema_version=self.persisted.loader.schema_version, history=self.history)
        return self.persisted.save_new_revision(self.persist_root, editable, note=note, make_active=make_active)
