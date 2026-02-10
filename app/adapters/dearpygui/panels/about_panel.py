# app/adapters/dearpygui/panels/about_panel.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from helpers.toolkits.ui.runtime.windows import ExtraStateHooks
from helpers.toolkits.ui.runtime.spec_resolve import resolve_window_factory_args


def build_toolkit_about_panel(host, ctx, window_id: str, parent_tag: str) -> ExtraStateHooks:
    """
    Toolkit reusable about panel.

    Args (factory_args / ref):
      title: str (default "About")
      lines: list[str] (default [])
      show_runtime_info: bool (default True)
    """
    dpg = host.dpg
    w = ctx.spec.get_window(window_id)
    helpers_root = _helpers_root_from_ctx(ctx)
    args = resolve_window_factory_args(w, helpers_root=helpers_root) if w else {}

    title = str(args.get("title", "About"))
    lines = args.get("lines", [])
    if not isinstance(lines, list):
        lines = []
    lines = [str(x) for x in lines]
    show_runtime_info = bool(args.get("show_runtime_info", True))

    state: Dict[str, Any] = {"profile": "Default"}
    combo_tag = f"{parent_tag}::profile"

    dpg.add_text(title, parent=parent_tag)
    dpg.add_separator(parent=parent_tag)

    for line in lines:
        dpg.add_text(line, parent=parent_tag)

    if show_runtime_info:
        dpg.add_separator(parent=parent_tag)
        dpg.add_text(f"Windows: {len(ctx.spec.windows)}", parent=parent_tag)
        dpg.add_text(f"Commands: {len(ctx.spec.commands)}", parent=parent_tag)

    dpg.add_separator(parent=parent_tag)
    dpg.add_text("Profile (persisted via WindowState.extra):", parent=parent_tag)
    dpg.add_combo(items=["Default", "Debug", "Minimal"], tag=combo_tag, default_value="Default", parent=parent_tag, width=200)

    def load_extra(extra: dict) -> None:
        state["profile"] = str(extra.get("profile", "Default"))
        dpg.set_value(combo_tag, state["profile"])

    def save_extra() -> dict:
        return {"profile": str(dpg.get_value(combo_tag))}

    return ExtraStateHooks(load_extra=load_extra, save_extra=save_extra)


def _helpers_root_from_ctx(ctx) -> Optional[Path]:
    v = ctx.state.kv.get("_helpers_root", None)
    return None if not v else Path(v)
