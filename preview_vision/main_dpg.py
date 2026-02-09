# preview_vision/main_dpg.py
# DearPyGui preview app (thin wiring layer): UI layout + button wiring + per-frame pump.
# Updated to use StageSurface + ViewportCompositor (drawlist-based) so video fits on window resize.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from helpers.runtime.optional_imports import require
from preview_vision.config_io import build_preview_wiring
from services.vision.preview_session import VisionPreviewSession

from app.adapters.dearpygui.vision.stage_surface import StageSurface, StageSurfaceSpec
from app.adapters.dearpygui.vision.dpg_texture_pool import DpgTexturePool
from app.adapters.dearpygui.vision.dpg_draw_backend import DpgDrawBackend
from app.adapters.dearpygui.vision.viewport_compositor import ViewportCompositor


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DearPyGui preview for helpers.vision capture sources.")
    p.add_argument("--config", default="preview_vision/config_capture.json", help="Path to capture config JSON.")
    p.add_argument("--runner-fps", type=float, default=30.0, help="Runner pacing FPS (0 disables).")
    p.add_argument("--title", default="Vision Preview", help="Window title.")
    return p.parse_args()


def _repo_root_from_this_file() -> Path:
    # preview_vision/main_dpg.py -> repo root is parent of preview_vision/
    return Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> Dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return raw


def main() -> int:
    dpg = require("dearpygui.dearpygui", pip_hint="dearpygui", purpose="Vision preview UI")

    args = parse_args()
    load_config, capture_config, build_source = build_preview_wiring()
    session = VisionPreviewSession(
        config_path=Path(args.config),
        runner_fps=args.runner_fps,
        load_config=load_config,
        capture_config=capture_config,
        build_source=build_source,
    )

    repo_root = _repo_root_from_this_file()

    # Defaults (seed-level) catalogs
    layer_catalog_path = repo_root / "helpers" / "configs" / "layers" / "default.json"
    anno_catalog_path = repo_root / "helpers" / "configs" / "vision" / "annotations" / "default.json"

    layer_catalog_raw = _load_json(layer_catalog_path)
    anno_catalog_raw = _load_json(anno_catalog_path)

    # UI tags
    info_tag = "txt_info"
    stats_tag = "txt_stats"
    status_tag = "txt_status"

    # Stage tags
    stage_spec = StageSurfaceSpec(
        stage_tag="stage",
        child_tag="stage.child",
        drawlist_tag="stage.drawlist",
    )

    def safe_call(fn, label: str):
        def _cb():
            try:
                fn()
                dpg.set_value(status_tag, f"{label}: OK")
            except Exception as e:
                dpg.set_value(status_tag, f"{label}: ERROR: {e!r}")
                print(f"{label} failed:", repr(e))
        return _cb

    dpg.create_context()
    dpg.create_viewport(title=args.title, width=1100, height=750)

    # Build window + stage
    with dpg.window(label=args.title, width=1080, height=720, tag="win.main"):
        dpg.add_text(f"Config: {args.config}")
        dpg.add_text("", tag=info_tag)
        dpg.add_text("", tag=stats_tag)
        dpg.add_text("", tag=status_tag)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Start", callback=safe_call(session.start, "Start"))
            dpg.add_button(label="Stop", callback=safe_call(session.stop, "Stop"))
            dpg.add_button(label="Pause/Resume", callback=safe_call(session.toggle_pause, "Pause/Resume"))
            dpg.add_button(label="Reload config", callback=safe_call(session.reload, "Reload"))
            dpg.add_button(label="Quit", callback=lambda: dpg.stop_dearpygui())

        stage = StageSurface(dpg=dpg, spec=stage_spec)
        stage.build()

    # Runtime render stack
    textures = DpgTexturePool(dpg=dpg, registry_tag="texreg.main")
    backend = DpgDrawBackend(dpg=dpg, drawlist_tag=stage.drawlist_tag)

    compositor = ViewportCompositor.from_raw_catalogs(
        dpg=dpg,
        stage=stage,
        textures=textures,
        backend=backend,
        layer_catalog_raw=layer_catalog_raw,
        annotation_catalog_raw=anno_catalog_raw,
    )

    dpg.setup_dearpygui()
    dpg.show_viewport()

    try:
        while dpg.is_dearpygui_running():
            rgb = session.poll_rgb()
            st = session.stats()

            # This now refits on resize because compositor:
            # - reads stage.surface_size()
            # - redraws when size changes even if rgb is None (cached frame path)
            compositor.render(
                rgb=rgb,
                debug_text=f"in={st.frames_in} out={st.frames_out} err={st.last_error}",
            )

            # Optional info line (kept minimal)
            info = compositor.info
            dpg.set_value(
                info_tag,
                f"src={info.src_w}x{info.src_h} surface={info.surface_w}x{info.surface_h} "
                f"fit={info.fit_mode} draw_rect={tuple(round(x, 1) for x in info.draw_rect_xywh)}",
            )
            dpg.set_value(stats_tag, f"in={st.frames_in} out={st.frames_out} err={st.last_error}")

            dpg.render_dearpygui_frame()
    finally:
        session.shutdown()
        dpg.destroy_context()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
