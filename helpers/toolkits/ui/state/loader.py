# helpers/toolkits/ui/state/loader.py
from __future__ import annotations

from helpers.persist.loader import CatalogLoader

from .model import UiState
from .serde import ensure_ui_state, dump_ui_state


def make_ui_state_catalog_loader(*, helpers_root=None) -> CatalogLoader[UiState]:
    """
    UI state uses the same CatalogLoader convention + schema hooks as the rest of the toolkit.
    """
    return CatalogLoader(
        app_name="ui",
        validate=ensure_ui_state,
        dump=dump_ui_state,
        schema_name="ui_state",
        schema_version=1,
        helpers_root=helpers_root,
    )
