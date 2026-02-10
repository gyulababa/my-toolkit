# services/ui/ui_state_service.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from helpers.catalog import EditableCatalog
from helpers.history.history import History
from helpers.persist.persisted_catalog_loader import PersistedCatalogLoader

from helpers.toolkits.ui.spec.models import UiSpec
from helpers.toolkits.ui.state.defaults import default_ui_state_from_spec
from helpers.toolkits.ui.state.loader import make_ui_state_catalog_loader
from helpers.toolkits.ui.state.models import UiState
from helpers.toolkits.ui.state.serde import ensure_ui_state, dump_ui_state


@dataclass
class UiStateService:
    """
    Persisted UI-state domain service.

    Domain layout:
      <persist root>/ui_state/index file
      <persist root>/ui_state/0001.json, 0002.json...

    The active doc is the "last state". Older docs are snapshots.
    """
    persist_root: Path
    spec: UiSpec
    helpers_root: Optional[Path] = None
    domain: str = "ui_state"

    def __post_init__(self) -> None:
        loader = make_ui_state_catalog_loader(helpers_root=self.helpers_root)

        # Seed doc: derived from UiSpec (windows, drawn_on_start)
        seed_state = default_ui_state_from_spec(self.spec)
        seed_fn = lambda: dump_ui_state(seed_state)

        self.persist = PersistedCatalogLoader(loader=loader, domain=self.domain, seed_raw=seed_fn)
        self.history = History()

    def load_active_editable(self) -> EditableCatalog[UiState]:
        return self.persist.load_active_editable(self.persist_root, history=self.history)

    def load_active_state(self) -> UiState:
        raw = self.persist.load_active_raw(self.persist_root)
        return ensure_ui_state(raw)

    def save_new_revision_from_state(
        self,
        state: UiState,
        *,
        note: Optional[str] = "ui autosave",
        make_active: bool = True,
    ) -> Path:
        editable = EditableCatalog(
            raw=dump_ui_state(state),
            schema_name="ui_state",
            schema_version=1,
            history=self.history,
        )
        return self.persist.save_new_revision(
            self.persist_root,
            editable,
            note=note,
            validate_before_save=True,
            make_active=make_active,
        )

    def promote_existing(self, doc_id: str, *, note: Optional[str] = None) -> None:
        self.persist.promote_existing(self.persist_root, doc_id, note=note)
