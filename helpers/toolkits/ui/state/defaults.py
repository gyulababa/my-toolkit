# helpers/toolkits/ui/state/defaults.py
from __future__ import annotations

from typing import Optional

from helpers.toolkits.ui.spec import UiSpec
from .model import UiState, WindowState


def default_ui_state_from_spec(spec: UiSpec) -> UiState:
    st = UiState(version=1, active_layout_id="default", dock_layout_blob=None)
    for w in spec.windows:
        st.windows[w.id] = WindowState(
            id=w.id,
            is_open=bool(w.drawn_on_start),
            pos_xy=None,
            size_wh=None,
            docked_to=None,
            extra={},
        )
    return st
