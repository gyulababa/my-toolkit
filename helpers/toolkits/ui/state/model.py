# helpers/toolkits/ui/state/model.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


@dataclass
class WindowState:
    id: str
    is_open: bool = True
    pos_xy: Optional[Tuple[int, int]] = None
    size_wh: Optional[Tuple[int, int]] = None
    # Adapter may store dock-related info here (optional)
    docked_to: Optional[str] = None
    # Window-specific extra state (adapter/factory-controlled)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UiState:
    version: int = 1
    active_layout_id: str = "default"
    # If adapter supports importing/exporting dock layout, store it here.
    dock_layout_blob: Optional[str] = None
    windows: Dict[str, WindowState] = field(default_factory=dict)
    # General app-level kv bag (last opened config, selected profile, etc.)
    kv: Dict[str, Any] = field(default_factory=dict)

    def get_window(self, window_id: str) -> WindowState:
        if window_id not in self.windows:
            self.windows[window_id] = WindowState(id=window_id, is_open=False)
        return self.windows[window_id]
