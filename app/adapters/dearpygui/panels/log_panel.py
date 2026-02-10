# app/adapters/dearpygui/panels/log_panel.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from helpers.toolkits.ui.runtime.windows import ExtraStateHooks
from helpers.toolkits.ui.runtime.spec_resolve import resolve_window_factory_args


def build_toolkit_log_panel(host, ctx, window_id: str, parent_tag: str) -> ExtraStateHooks:
    """
    Toolkit reusable log panel.

    Args (factory_args / ref):
      bind_text_kv: str (default "log.text")
      max_lines: int (default 5000)
      show_scroll_lock: bool (default True)
      show_clear_button: bool (default True)
      clear_command_id: str | null (default null)
    """
    dpg = host.dpg
    w = ctx.spec.get_window(window_id)
    helpers_root = _helpers_root_from_ctx(ctx)

    args = resolve_window_factory_args(w, helpers_root=helpers_root) if w else {}
    bind_text_kv = str(args.get("bind_text_kv", "log.text"))
    max_lines = int(args.get("max_lines", 5000))
    show_scroll_lock = bool(args.get("show_scroll_lock", True))
    show_clear_button = bool(args.get("show_clear_button", True))
    clear_command_id = args.get("clear_command_id", None)

    state: Dict[str, Any] = {"scroll_lock": False}

    chk_tag = f"{parent_tag}::scroll_lock"
    btn_tag = f"{parent_tag}::clear_btn"
    txt_tag = f"{parent_tag}::log_text"

    if show_scroll_lock:
        dpg.add_checkbox(label="Scroll lock", tag=chk_tag, default_value=False, parent=parent_tag)

    if show_clear_button:
        def _on_clear(*_a, **_k) -> None:
            if clear_command_id:
                ctx.events.emit("state_dirty", reason="log_clear_button")
                ctx.host.request_quit() if False else None  # no-op placeholder
                # Execute command via registry is not available here; apps can bind button to kv too.
                # Preferred: provide a command button via menu; or implement a host-level dispatch later.
            # Fallback: clear kv
            ctx.state.kv[bind_text_kv] = ""
            ctx.events.emit("state_dirty", reason="log_clear_fallback")

        dpg.add_button(label="Clear", tag=btn_tag, callback=_on_clear, parent=parent_tag)

    initial_text = str(ctx.state.kv.get(bind_text_kv, ""))
    dpg.add_input_text(
        tag=txt_tag,
        label="",
        multiline=True,
        readonly=True,
        width=-1,
        height=260,
        default_value=_trim_lines(initial_text, max_lines=max_lines),
        parent=parent_tag,
    )

    def load_extra(extra: dict) -> None:
        state["scroll_lock"] = bool(extra.get("scroll_lock", False))
        if show_scroll_lock:
            dpg.set_value(chk_tag, state["scroll_lock"])
        # Refresh displayed text from kv on load
        cur = str(ctx.state.kv.get(bind_text_kv, ""))
        dpg.set_value(txt_tag, _trim_lines(cur, max_lines=max_lines))

    def save_extra() -> dict:
        out = {}
        if show_scroll_lock:
            out["scroll_lock"] = bool(dpg.get_value(chk_tag))
        return out

    return ExtraStateHooks(load_extra=load_extra, save_extra=save_extra)


def _trim_lines(s: str, *, max_lines: int) -> str:
    if max_lines <= 0:
        return s
    lines = s.splitlines()
    if len(lines) <= max_lines:
        return s
    return "\n".join(lines[-max_lines:]) + "\n"


def _helpers_root_from_ctx(ctx) -> Optional[Path]:
    v = ctx.state.kv.get("_helpers_root", None)
    return None if not v else Path(v)
