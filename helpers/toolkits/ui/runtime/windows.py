# helpers/toolkits/ui/runtime/windows.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Protocol

from helpers.toolkits.ui.spec import WindowSpec
from helpers.toolkits.ui.state import WindowState


class WindowHandle(Protocol):
    window_id: str

    def set_open(self, is_open: bool) -> None: ...
    def is_open(self) -> bool: ...

    def apply_state(self, state: WindowState) -> None: ...
    def capture_state(self) -> WindowState: ...


@dataclass(frozen=True)
class ExtraStateHooks:
    """
    Optional per-window extra-state hooks.
    Stored under WindowState.extra (a dict).
    """
    load_extra: Callable[[dict], None]
    save_extra: Callable[[], dict]


class UiHost(Protocol):
    """
    Frontend adapter interface.
    """
    def create_window(self, spec: WindowSpec, factory_key: str, ctx: Any) -> WindowHandle: ...
    def build_menus(self, spec_menus: Any, on_command: Any, on_window_toggle: Any) -> None: ...
    def request_quit(self) -> None: ...


# Factory builds content inside a given parent container/tag.
# It may return extra-state hooks (optional).
WindowBuildFn = Callable[[UiHost, Any, str, str], Optional[ExtraStateHooks]]


@dataclass
class _FactoryEntry:
    fn: WindowBuildFn


class WindowFactoryRegistry:
    def __init__(self) -> None:
        self._factories: Dict[str, _FactoryEntry] = {}

    def register(self, factory_key: str, fn: WindowBuildFn) -> None:
        if factory_key in self._factories:
            raise ValueError(f"Factory already registered: {factory_key}")
        self._factories[factory_key] = _FactoryEntry(fn=fn)

    def build(self, factory_key: str, host: UiHost, ctx: Any, window_id: str, parent_tag: str) -> Optional[ExtraStateHooks]:
        ent = self._factories.get(factory_key)
        if ent is None:
            raise KeyError(f"Unknown factory key: {factory_key}")
        return ent.fn(host, ctx, window_id, parent_tag)

    def has(self, factory_key: str) -> bool:
        return factory_key in self._factories
