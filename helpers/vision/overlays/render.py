# helpers/vision/overlays/render.py
# Toolkit-agnostic layer rendering logic, driven by LayerCatalog + AnnotationCatalog.
# The DPG backend implements the primitive calls.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from helpers.vision.overlays.fit import FitTransform
from helpers.vision.overlays.filters import filter_annotations
from helpers.vision.overlays.models import (
    Annotation,
    GuidesAnnotation,
    LayerCatalog,
    LayerSpec,
    RectAnnotation,
    StylePreset,
    TextAnnotation,
)

RGBA = Tuple[int, int, int, int]


@dataclass(frozen=True)
class RenderContext:
    xf: FitTransform
    style_presets: Dict[str, StylePreset]
    layer: LayerSpec


class DrawBackendProto:
    # minimal protocol; DPG backend matches this
    def clear(self) -> None: ...
    def image(self, tex_ref, *, pmin, pmax, tint=None) -> None: ...
    def rect(self, *, pmin, pmax, stroke=None, fill=None) -> None: ...
    def line(self, p1, p2, *, stroke=None) -> None: ...
    def polyline(self, points, *, closed=False, stroke=None) -> None: ...
    def text(self, pos, text: str, *, style=None) -> None: ...


def render_layers(
    *,
    backend: DrawBackendProto,
    layer_catalog: LayerCatalog,
    annotations: List[Annotation],
    xf: FitTransform,
    video_tex_ref,
    extra_text: Optional[str] = None,
) -> None:
    """
    Render layer stack in z-order.

    - video_tex_ref is required for the "video" layer.
    - annotations come from AnnotationCatalog.active_annotations() + ephemeral detections, etc.
    """
    presets = layer_catalog.style_presets

    for layer in layer_catalog.sorted_layers():
        if not layer.enabled:
            continue

        ctx = RenderContext(xf=xf, style_presets=presets, layer=layer)

        if layer.kind == "video":
            _render_video_layer(backend, ctx, video_tex_ref)
            continue

        # filter annotations for this layer
        anns = filter_annotations(annotations, layer.filters)

        if layer.id == "guides" or (layer.filters.kinds and "guides" in layer.filters.kinds):
            _render_guides_layer(backend, ctx, anns)
            continue

        # generic render by annotation kind
        for a in anns:
            if a.kind in ("bbox", "roi") and isinstance(a, RectAnnotation):
                _render_rect_anno(backend, ctx, a)
            elif a.kind == "text" and isinstance(a, TextAnnotation):
                _render_text_anno(backend, ctx, a)

        # optional HUD injection
        if extra_text and layer.id == "debug_text":
            _render_debug_hud(backend, ctx, extra_text)


# ---------------------------
# per-layer renderers
# ---------------------------

def _render_video_layer(backend: DrawBackendProto, ctx: RenderContext, video_tex_ref) -> None:
    dr = ctx.xf.draw_rect
    backend.image(video_tex_ref, pmin=(dr.x, dr.y), pmax=(dr.x + dr.w, dr.y + dr.h))


def _style_for(ctx: RenderContext, a: Annotation, *, for_text: bool = False) -> StylePreset:
    # layer preset
    s = StylePreset()
    if ctx.layer.style.preset and ctx.layer.style.preset in ctx.style_presets:
        s = s.merged(ctx.style_presets[ctx.layer.style.preset])

    # layer overrides
    s = s.merged(ctx.layer.style.overrides)

    # by_label
    label = None
    if isinstance(a.meta, dict):
        label = a.meta.get("label", None)
    if isinstance(label, str) and label in ctx.layer.style.by_label:
        s = s.merged(ctx.layer.style.by_label[label])

    # per-annotation style
    if a.style:
        s = s.merged(a.style)

    # if text style preset configured for labels
    if for_text and ctx.layer.render.label_style_preset and ctx.layer.render.label_style_preset in ctx.style_presets:
        s = s.merged(ctx.style_presets[ctx.layer.render.label_style_preset])

    return s


def _render_rect_anno(backend: DrawBackendProto, ctx: RenderContext, a: RectAnnotation) -> None:
    # rect coords
    if a.space == "norm":
        p1 = ctx.xf.norm_to_surface(a.rect.x, a.rect.y)
        p2 = ctx.xf.norm_to_surface(a.rect.x + a.rect.w, a.rect.y + a.rect.h)
    else:
        p1 = ctx.xf.src_to_surface(a.rect.x, a.rect.y)
        p2 = ctx.xf.src_to_surface(a.rect.x + a.rect.w, a.rect.y + a.rect.h)

    style = _style_for(ctx, a, for_text=False)

    stroke_rgba = style.stroke_rgba or (255, 255, 255, 255)
    fill_rgba = style.fill_rgba or (0, 0, 0, 0)
    stroke_w = float(style.stroke_width or 1.0)

    backend.rect(
        pmin=p1,
        pmax=p2,
        stroke={"color": stroke_rgba, "thickness": stroke_w},
        fill={"color": fill_rgba},
    )

    if ctx.layer.render.draw_labels:
        _render_rect_label(backend, ctx, a, p1, p2)


def _render_rect_label(backend: DrawBackendProto, ctx: RenderContext, a: RectAnnotation, p1, p2) -> None:
    # Label text fields
    meta = a.meta if isinstance(a.meta, dict) else {}
    label = meta.get("label", a.name or a.id)
    conf = meta.get("conf", meta.get("confidence", None))
    name = a.name or meta.get("name", None)

    # format map
    fm = {
        "id": a.id,
        "label": label if label is not None else "",
        "conf": float(conf) if isinstance(conf, (int, float)) else 0.0,
        "name": name if name is not None else "",
    }
    try:
        text = ctx.layer.render.label_format.format(**fm)
    except Exception:
        text = str(fm.get("label", ""))

    # anchor
    ax, ay = p1
    bx, by = p2
    anchor = ctx.layer.render.label_anchor
    if anchor == "top_left":
        pos = (ax + 2.0, ay + 2.0)
    elif anchor == "bottom_left":
        pos = (ax + 2.0, by - 18.0)
    elif anchor == "top_right":
        pos = (bx - 2.0, ay + 2.0)
    else:  # bottom_right
        pos = (bx - 2.0, by - 18.0)

    style = _style_for(ctx, a, for_text=True)
    text_rgba = style.text_rgba or (255, 255, 255, 255)
    font_px = int(style.font_px or 16)

    # shadow (optional)
    if style.shadow_rgba and style.shadow_offset_px:
        sx, sy = style.shadow_offset_px
        backend.text((pos[0] + sx, pos[1] + sy), text, style={"color": style.shadow_rgba, "size": font_px})

    backend.text(pos, text, style={"color": text_rgba, "size": font_px})


def _render_text_anno(backend: DrawBackendProto, ctx: RenderContext, a: TextAnnotation) -> None:
    if a.space == "norm":
        pos = ctx.xf.norm_to_surface(a.anchor[0], a.anchor[1])
    else:
        pos = ctx.xf.src_to_surface(a.anchor[0], a.anchor[1])

    style = _style_for(ctx, a, for_text=True)
    text_rgba = style.text_rgba or (255, 255, 255, 255)
    font_px = int(style.font_px or 16)

    if style.shadow_rgba and style.shadow_offset_px:
        sx, sy = style.shadow_offset_px
        backend.text((pos[0] + sx, pos[1] + sy), a.text, style={"color": style.shadow_rgba, "size": font_px})

    backend.text(pos, a.text, style={"color": text_rgba, "size": font_px})


def _render_guides_layer(backend: DrawBackendProto, ctx: RenderContext, anns: List[Annotation]) -> None:
    # Guides can come from:
    #  - layer.render.{rule_of_thirds,crosshair,safe_margin_pct}
    #  - guides annotations (merge / OR)
    rule_of_thirds = ctx.layer.render.rule_of_thirds
    crosshair = ctx.layer.render.crosshair
    safe_margin_pct = ctx.layer.render.safe_margin_pct

    for a in anns:
        if isinstance(a, GuidesAnnotation):
            g = a.guides or {}
            rule_of_thirds = rule_of_thirds or bool(g.get("rule_of_thirds", False))
            crosshair = crosshair or bool(g.get("crosshair", False))
            try:
                safe_margin_pct = max(safe_margin_pct, float(g.get("safe_margin_pct", 0.0) or 0.0))
            except Exception:
                pass

    # style
    style = StylePreset()
    if ctx.layer.style.preset and ctx.layer.style.preset in ctx.style_presets:
        style = style.merged(ctx.style_presets[ctx.layer.style.preset])
    style = style.merged(ctx.layer.style.overrides)

    stroke_rgba = style.stroke_rgba or (255, 255, 255, 120)
    stroke_w = float(style.stroke_width or 1.0)

    dr = ctx.xf.draw_rect
    x0, y0, w, h = dr.x, dr.y, dr.w, dr.h
    x1, y1 = x0 + w, y0 + h

    if safe_margin_pct > 0.0:
        mx = w * safe_margin_pct
        my = h * safe_margin_pct
        backend.rect(
            pmin=(x0 + mx, y0 + my),
            pmax=(x1 - mx, y1 - my),
            stroke={"color": stroke_rgba, "thickness": stroke_w},
            fill={"color": (0, 0, 0, 0)},
        )

    if rule_of_thirds:
        # vertical thirds
        backend.line((x0 + w / 3.0, y0), (x0 + w / 3.0, y1), stroke={"color": stroke_rgba, "thickness": stroke_w})
        backend.line((x0 + 2.0 * w / 3.0, y0), (x0 + 2.0 * w / 3.0, y1), stroke={"color": stroke_rgba, "thickness": stroke_w})
        # horizontal thirds
        backend.line((x0, y0 + h / 3.0), (x1, y0 + h / 3.0), stroke={"color": stroke_rgba, "thickness": stroke_w})
        backend.line((x0, y0 + 2.0 * h / 3.0), (x1, y0 + 2.0 * h / 3.0), stroke={"color": stroke_rgba, "thickness": stroke_w})

    if crosshair:
        backend.line((x0 + w / 2.0, y0), (x0 + w / 2.0, y1), stroke={"color": stroke_rgba, "thickness": stroke_w})
        backend.line((x0, y0 + h / 2.0), (x1, y0 + h / 2.0), stroke={"color": stroke_rgba, "thickness": stroke_w})


def _render_debug_hud(backend: DrawBackendProto, ctx: RenderContext, text: str) -> None:
    # Place at top-left of surface (not draw_rect). This is deliberate.
    style = StylePreset()
    if ctx.layer.style.preset and ctx.layer.style.preset in ctx.style_presets:
        style = style.merged(ctx.style_presets[ctx.layer.style.preset])
    style = style.merged(ctx.layer.style.overrides)

    text_rgba = style.text_rgba or (255, 255, 255, 255)
    font_px = int(style.font_px or 16)

    backend.text((10.0, 10.0), text, style={"color": text_rgba, "size": font_px})
