# app/adapters/dearpygui/vision/viewport_compositor.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

from helpers.vision.imaging_buffers import rgb_to_rgba_u8
from helpers.vision.overlays.fit import FitTransform
from helpers.vision.overlays.models import (
    Annotation,
    AnnotationCatalog,
    FitMode,
    LayerCatalog,
    load_annotation_catalog,
    load_layer_catalog,
)
from helpers.vision.overlays.render import render_layers

from app.adapters.dearpygui.vision.stage_surface import StageSurface
from app.adapters.dearpygui.vision.dpg_draw_backend import DpgDrawBackend
from app.adapters.dearpygui.vision.dpg_texture_pool import DpgTexturePool, TextureRef


@dataclass
class ViewportFrameInfo:
    src_w: int = 0
    src_h: int = 0
    surface_w: int = 0
    surface_h: int = 0
    fit_mode: FitMode = "contain"
    draw_rect_xywh: Tuple[float, float, float, float] = (0, 0, 0, 0)


class ViewportCompositor:
    """
    Per-frame orchestrator for video + composited overlay layers.

    Inputs:
      - rgb frame (HxWx3 u8) OR None (no new frame this tick)
      - LayerCatalog (from layer_catalog.json)
      - AnnotationCatalog (from annotation_catalog.json)
      - optional ephemeral annotations (detections, etc.)

    Output:
      - Drawlist contents updated

    Key behavior:
      - Redraws not only when a new frame arrives, but also when the stage surface size changes
        (so window resize refits even if the capture source doesn't deliver a new frame immediately).
    """

    def __init__(
        self,
        *,
        dpg,
        stage: StageSurface,
        textures: DpgTexturePool,
        backend: DpgDrawBackend,
        layer_catalog: LayerCatalog,
        annotation_catalog: AnnotationCatalog,
    ):
        self._dpg = dpg
        self.stage = stage
        self.textures = textures
        self.backend = backend

        self.layer_catalog = layer_catalog
        self.annotation_catalog = annotation_catalog

        self.info = ViewportFrameInfo()

        # Cached state for resize-triggered redraws
        self._last_rgb: Optional[np.ndarray] = None
        self._last_surface_size: Tuple[int, int] = (0, 0)

        # ensure base video texture exists
        self.textures.ensure("video", size=(2, 2))

    @staticmethod
    def from_raw_catalogs(
        *,
        dpg,
        stage: StageSurface,
        textures: DpgTexturePool,
        backend: DpgDrawBackend,
        layer_catalog_raw: dict,
        annotation_catalog_raw: dict,
    ) -> "ViewportCompositor":
        return ViewportCompositor(
            dpg=dpg,
            stage=stage,
            textures=textures,
            backend=backend,
            layer_catalog=load_layer_catalog(layer_catalog_raw),
            annotation_catalog=load_annotation_catalog(annotation_catalog_raw),
        )

    def set_catalogs(self, *, layer_catalog: Optional[LayerCatalog] = None, annotation_catalog: Optional[AnnotationCatalog] = None) -> None:
        if layer_catalog is not None:
            self.layer_catalog = layer_catalog
        if annotation_catalog is not None:
            self.annotation_catalog = annotation_catalog

    def render(
        self,
        *,
        rgb: Optional[np.ndarray],
        extra_annotations: Optional[List[Annotation]] = None,
        debug_text: Optional[str] = None,
    ) -> None:
        """
        Render one tick.

        - If `rgb` is provided, it becomes the cached last frame and is rendered.
        - If `rgb` is None, we still may re-render if the stage surface size changed.
        """
        # Always read surface size first (resize-driven redraw depends on it)
        surface_w, surface_h = self.stage.surface_size()
        if surface_w <= 0 or surface_h <= 0:
            return

        surface_size = (surface_w, surface_h)
        surface_changed = surface_size != self._last_surface_size
        self._last_surface_size = surface_size

        # Ensure drawlist matches stage size (DPG doesn't always propagate -1 sizing perfectly)
        try:
            self._dpg.configure_item(self.stage.drawlist_tag, width=surface_w, height=surface_h)
        except Exception:
            # If item isn't built yet or DPG rejects, just proceed; next tick will try again.
            pass

        # Cache incoming frame if present
        if rgb is not None:
            if rgb.ndim != 3 or rgb.shape[2] != 3:
                raise ValueError(f"ViewportCompositor.render: expected RGB HxWx3, got {getattr(rgb, 'shape', None)!r}")
            self._last_rgb = rgb

        # If we have no frame cached yet, nothing to draw
        if self._last_rgb is None:
            return

        # If there's no new frame and no resize, skip work
        if rgb is None and not surface_changed:
            return

        # Render using cached frame (either new this tick or last known frame)
        rgb_use = self._last_rgb
        h, w, _ = rgb_use.shape

        fit_mode = str(self.layer_catalog.viewport.get("fit_mode", "contain"))
        if fit_mode not in ("contain", "cover", "stretch"):
            fit_mode = "contain"

        xf = FitTransform.compute(src_w=w, src_h=h, surface_w=surface_w, surface_h=surface_h, mode=fit_mode)  # type: ignore[arg-type]

        # Upload frame
        rgba = rgb_to_rgba_u8(rgb_use)
        video_ref: TextureRef = self.textures.update_rgba_u8("video", rgba, allow_resize=True)

        # Combine annotations
        annotations: List[Annotation] = []
        annotations.extend(self.annotation_catalog.active_annotations())
        if extra_annotations:
            annotations.extend(extra_annotations)

        # Clear + render
        self.backend.clear()

        # optional background
        bg = self.layer_catalog.viewport.get("background_rgba", [0, 0, 0, 255])
        show_letterbox = bool(self.layer_catalog.viewport.get("show_letterbox", True))
        if show_letterbox and isinstance(bg, list) and len(bg) == 4:
            # Fill the entire surface rect before drawing video
            self.backend.rect(
                pmin=(0.0, 0.0),
                pmax=(float(surface_w), float(surface_h)),
                stroke={"color": (0, 0, 0, 0), "thickness": 0.0},
                fill={"color": (int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]))},
            )

        render_layers(
            backend=self.backend,
            layer_catalog=self.layer_catalog,
            annotations=annotations,
            xf=xf,
            video_tex_ref=video_ref,
            extra_text=debug_text,
        )

        # update info snapshot (for UI text)
        self.info = ViewportFrameInfo(
            src_w=w,
            src_h=h,
            surface_w=surface_w,
            surface_h=surface_h,
            fit_mode=fit_mode,  # type: ignore[arg-type]
            draw_rect_xywh=(xf.draw_rect.x, xf.draw_rect.y, xf.draw_rect.w, xf.draw_rect.h),
        )
