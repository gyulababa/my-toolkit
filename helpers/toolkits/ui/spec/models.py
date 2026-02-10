# helpers/toolkits/ui/spec/models.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Union


CommandKind = Literal["app", "builtin", "runtime"]


@dataclass(frozen=True)
class CommandSpec:
    id: str
    title: str
    kind: CommandKind = "app"
    # Optional payload schema name / hint (kept loose for v1)
    payload_schema: Optional[str] = None
    # Optional enable predicate key (resolved by runtime/registry)
    enabled_when: Optional[str] = None


MenuItemType = Literal["command", "submenu", "separator", "window_toggle"]


@dataclass(frozen=True)
class MenuItemCommand:
    type: Literal["command"]
    command_id: str


@dataclass(frozen=True)
class MenuItemSubmenu:
    type: Literal["submenu"]
    title: str
    items: List["MenuItem"]


@dataclass(frozen=True)
class MenuItemSeparator:
    type: Literal["separator"]


@dataclass(frozen=True)
class MenuItemWindowToggle:
    type: Literal["window_toggle"]
    window_id: str


MenuItem = Union[MenuItemCommand, MenuItemSubmenu, MenuItemSeparator, MenuItemWindowToggle]


@dataclass(frozen=True)
class MenuSpec:
    id: str
    title: str
    items: List[MenuItem]


DockArea = Literal["left", "right", "top", "bottom", "center"]


@dataclass(frozen=True)
class DockHint:
    area: DockArea = "center"
    # Ratio of dock area (adapter may interpret). Optional.
    ratio: Optional[float] = None
    # Optional dock relative to another window (adapter may interpret)
    target_window_id: Optional[str] = None


@dataclass(frozen=True)
class WindowSpec:
    id: str
    title: str
    factory: str
    drawn_on_start: bool = True
    dock_hint: Optional[DockHint] = None
    # Optional menu path hint (adapter may use). Example: ["View"]
    menu_path: Optional[List[str]] = None


@dataclass(frozen=True)
class UiSpec:
    version: int
    commands: List[CommandSpec] = field(default_factory=list)
    menus: List[MenuSpec] = field(default_factory=list)
    windows: List[WindowSpec] = field(default_factory=list)

    def command_ids(self) -> set[str]:
        return {c.id for c in self.commands}

    def window_ids(self) -> set[str]:
        return {w.id for w in self.windows}

    def get_window(self, window_id: str) -> Optional[WindowSpec]:
        for w in self.windows:
            if w.id == window_id:
                return w
        return None
