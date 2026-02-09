# helpers/vision/overlays/models.py
# Frontend-agnostic overlay models + catalog doc shapes (minimal, strict enough for runtime).

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple

from helpers.geometry.rect import RectF


FitMode = Literal["contain", "cover", "stretch"]
LayerKind = Literal["video", "texture", "vector", "mixed"]
AnnoKind = Literal["bbox", "roi", "polyline", "points", "text", "guides", "mask"]


RGBA = Tuple[int, int, int, int]
Point = Tuple[float, float]


@dataclass(frozen=True)
class StylePreset:
    # Vector
    stroke_rgba: Optional[RGBA] = None
    fill_rgba: Optional[RGBA] = None
    stroke_width: Optional[float] = None

    # Text
    text_rgba: Optional[RGBA] = None
    font_px: Optional[int] = None
    shadow_rgba: Optional[RGBA] = None
    shadow_offset_px: Optional[Tuple[int, int]] = None

    def merged(self, other: "StylePreset") -> "StylePreset":
        """Overlay `other` on top of self (other wins if not None)."""
        return StylePreset(
            stroke_rgba=other.stroke_rgba if other.stroke_rgba is not None else self.stroke_rgba,
            fill_rgba=other.fill_rgba if other.fill_rgba is not None else self.fill_rgba,
            stroke_width=other.stroke_width if other.stroke_width is not None else self.stroke_width,
            text_rgba=other.text_rgba if other.text_rgba is not None else self.text_rgba,
            font_px=other.font_px if other.font_px is not None else self.font_px,
            shadow_rgba=other.shadow_rgba if other.shadow_rgba is not None else self.shadow_rgba,
            shadow_offset_px=other.shadow_offset_px if other.shadow_offset_px is not None else self.shadow_offset_px,
        )

    @staticmethod
    def from_raw(raw: Any) -> "StylePreset":
        if not isinstance(raw, dict):
            return StylePreset()
        return StylePreset(
            stroke_rgba=_rgba_opt(raw.get("stroke_rgba")),
            fill_rgba=_rgba_opt(raw.get("fill_rgba")),
            stroke_width=_float_opt(raw.get("stroke_width")),
            text_rgba=_rgba_opt(raw.get("text_rgba")),
            font_px=_int_opt(raw.get("font_px")),
            shadow_rgba=_rgba_opt(raw.get("shadow_rgba")),
            shadow_offset_px=_pt_int2_opt(raw.get("shadow_offset_px")),
        )


@dataclass(frozen=True)
class Annotation:
    id: str
    kind: AnnoKind
    space: Literal["src", "norm"] = "src"
    tags: List[str] = field(default_factory=list)
    style: StylePreset = field(default_factory=StylePreset)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RectAnnotation(Annotation):
    rect: RectF = field(default_factory=lambda: RectF(0, 0, 0, 0))
    name: Optional[str] = None  # for ROI labels


@dataclass(frozen=True)
class TextAnnotation(Annotation):
    anchor: Point = (0.0, 0.0)
    text: str = ""


@dataclass(frozen=True)
class GuidesAnnotation(Annotation):
    guides: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AnnotationSet:
    id: str
    name: str
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    annotations: List[Annotation] = field(default_factory=list)


@dataclass(frozen=True)
class AnnotationCatalog:
    schema: str
    meta: Dict[str, Any]
    sets: List[AnnotationSet]

    def active_annotations(self) -> List[Annotation]:
        out: List[Annotation] = []
        for s in self.sets:
            if s.enabled:
                out.extend(s.annotations)
        return out


@dataclass(frozen=True)
class LayerFilter:
    kinds: Optional[List[AnnoKind]] = None
    require_tags_any: Optional[List[str]] = None
    require_tags_all: Optional[List[str]] = None
    exclude_tags_any: Optional[List[str]] = None

    @staticmethod
    def from_raw(raw: Any) -> "LayerFilter":
        if not isinstance(raw, dict):
            return LayerFilter()
        return LayerFilter(
            kinds=_list_str_opt(raw.get("kinds")),
            require_tags_any=_list_str_opt(raw.get("require_tags_any")),
            require_tags_all=_list_str_opt(raw.get("require_tags_all")),
            exclude_tags_any=_list_str_opt(raw.get("exclude_tags_any")),
        )


@dataclass(frozen=True)
class LayerStyle:
    preset: Optional[str] = None
    overrides: StylePreset = field(default_factory=StylePreset)
    by_label: Dict[str, StylePreset] = field(default_factory=dict)

    @staticmethod
    def from_raw(raw: Any) -> "LayerStyle":
        if not isinstance(raw, dict):
            return LayerStyle()
        by_label_raw = raw.get("by_label", {})
        by_label: Dict[str, StylePreset] = {}
        if isinstance(by_label_raw, dict):
            for k, v in by_label_raw.items():
                by_label[str(k)] = StylePreset.from_raw(v)
        return LayerStyle(
            preset=str(raw["preset"]) if isinstance(raw.get("preset"), str) else None,
            overrides=StylePreset.from_raw(raw.get("overrides")),
            by_label=by_label,
        )


@dataclass(frozen=True)
class LayerRenderOptions:
    draw_labels: bool = False
    label_format: str = "{label}"
    label_anchor: Literal["top_left", "bottom_left", "top_right", "bottom_right"] = "top_left"
    label_style_preset: Optional[str] = None

    # Guides options (if layer kind=guides or guides annotations are used)
    rule_of_thirds: bool = False
    crosshair: bool = False
    safe_margin_pct: float = 0.0

    @staticmethod
    def from_raw(raw: Any) -> "LayerRenderOptions":
        if not isinstance(raw, dict):
            return LayerRenderOptions()
        return LayerRenderOptions(
            draw_labels=bool(raw.get("draw_labels", False)),
            label_format=str(raw.get("label_format", "{label}")),
            label_anchor=str(raw.get("label_anchor", "top_left")),  # keep tolerant
            label_style_preset=str(raw["label_style_preset"]) if isinstance(raw.get("label_style_preset"), str) else None,
            rule_of_thirds=bool(raw.get("rule_of_thirds", False)),
            crosshair=bool(raw.get("crosshair", False)),
            safe_margin_pct=float(raw.get("safe_margin_pct", 0.0) or 0.0),
        )


@dataclass(frozen=True)
class LayerSource:
    type: Literal["frame", "mask"] = "frame"
    mask_id: Optional[str] = None

    @staticmethod
    def from_raw(raw: Any) -> "LayerSource":
        if not isinstance(raw, dict):
            return LayerSource()
        t = raw.get("type", "frame")
        if t not in ("frame", "mask"):
            t = "frame"
        return LayerSource(type=t, mask_id=str(raw["mask_id"]) if isinstance(raw.get("mask_id"), str) else None)


@dataclass(frozen=True)
class LayerSpec:
    id: str
    name: str
    kind: LayerKind
    z: int
    enabled: bool = True
    opacity: float = 1.0
    source: LayerSource = field(default_factory=LayerSource)
    filters: LayerFilter = field(default_factory=LayerFilter)
    style: LayerStyle = field(default_factory=LayerStyle)
    render: LayerRenderOptions = field(default_factory=LayerRenderOptions)


@dataclass(frozen=True)
class LayerCatalog:
    schema: str
    meta: Dict[str, Any]
    viewport: Dict[str, Any]
    style_presets: Dict[str, StylePreset]
    layers: List[LayerSpec]

    def sorted_layers(self) -> List[LayerSpec]:
        return sorted(self.layers, key=lambda l: (l.z, l.id))


# ----------------------------
# Parsing helpers
# ----------------------------

def load_layer_catalog(raw: Dict[str, Any]) -> LayerCatalog:
    schema = str(raw.get("schema", ""))
    viewport = raw.get("viewport", {}) if isinstance(raw.get("viewport"), dict) else {}
    meta = raw.get("meta", {}) if isinstance(raw.get("meta"), dict) else {}

    sp_raw = raw.get("style_presets", {})
    style_presets: Dict[str, StylePreset] = {}
    if isinstance(sp_raw, dict):
        for k, v in sp_raw.items():
            style_presets[str(k)] = StylePreset.from_raw(v)

    layers_raw = raw.get("layers", [])
    layers: List[LayerSpec] = []
    if isinstance(layers_raw, list):
        for item in layers_raw:
            if not isinstance(item, dict):
                continue
            layers.append(
                LayerSpec(
                    id=str(item.get("id", "")),
                    name=str(item.get("name", "")),
                    kind=str(item.get("kind", "vector")),  # tolerant
                    z=int(item.get("z", 0)),
                    enabled=bool(item.get("enabled", True)),
                    opacity=float(item.get("opacity", 1.0) or 1.0),
                    source=LayerSource.from_raw(item.get("source")),
                    filters=LayerFilter.from_raw(item.get("filters")),
                    style=LayerStyle.from_raw(item.get("style")),
                    render=LayerRenderOptions.from_raw(item.get("render")),
                )
            )

    # Basic sanity: drop empty ids
    layers = [l for l in layers if l.id]
    return LayerCatalog(schema=schema, meta=meta, viewport=viewport, style_presets=style_presets, layers=layers)


def load_annotation_catalog(raw: Dict[str, Any]) -> AnnotationCatalog:
    schema = str(raw.get("schema", ""))
    meta = raw.get("meta", {}) if isinstance(raw.get("meta"), dict) else {}
    sets_raw = raw.get("sets", [])
    sets_out: List[AnnotationSet] = []

    if isinstance(sets_raw, list):
        for s in sets_raw:
            if not isinstance(s, dict):
                continue
            ann_raw = s.get("annotations", [])
            ann_list: List[Annotation] = []
            if isinstance(ann_raw, list):
                for a in ann_raw:
                    if isinstance(a, dict):
                        ann_list.append(_parse_annotation(a))
            sets_out.append(
                AnnotationSet(
                    id=str(s.get("id", "")),
                    name=str(s.get("name", "")),
                    enabled=bool(s.get("enabled", True)),
                    tags=_list_str_opt(s.get("tags")) or [],
                    annotations=ann_list,
                )
            )

    sets_out = [s for s in sets_out if s.id]
    return AnnotationCatalog(schema=schema, meta=meta, sets=sets_out)


def _parse_annotation(a: Dict[str, Any]) -> Annotation:
    kind = str(a.get("kind", "bbox"))
    if kind not in ("bbox", "roi", "polyline", "points", "text", "guides", "mask"):
        kind = "bbox"

    base_kwargs = dict(
        id=str(a.get("id", "")),
        kind=kind,  # type: ignore[assignment]
        space=str(a.get("space", "src")),
        tags=_list_str_opt(a.get("tags")) or [],
        style=StylePreset.from_raw(a.get("style")),
        meta={k: v for k, v in a.items() if k not in ("id", "kind", "space", "tags", "style", "rect", "name", "anchor", "text", "guides")},
    )

    if kind in ("bbox", "roi"):
        r = a.get("rect", {})
        rect = RectF(
            x=float(r.get("x", 0.0) or 0.0),
            y=float(r.get("y", 0.0) or 0.0),
            w=float(r.get("w", 0.0) or 0.0),
            h=float(r.get("h", 0.0) or 0.0),
        )
        return RectAnnotation(
            **base_kwargs,  # type: ignore[arg-type]
            rect=rect,
            name=str(a.get("name")) if isinstance(a.get("name"), str) else None,
        )

    if kind == "text":
        anchor = a.get("anchor", [0.0, 0.0])
        if isinstance(anchor, (list, tuple)) and len(anchor) >= 2:
            p = (float(anchor[0]), float(anchor[1]))
        else:
            p = (0.0, 0.0)
        return TextAnnotation(
            **base_kwargs,  # type: ignore[arg-type]
            anchor=p,
            text=str(a.get("text", "")),
        )

    if kind == "guides":
        g = a.get("guides", {})
        return GuidesAnnotation(
            **base_kwargs,  # type: ignore[arg-type]
            guides=g if isinstance(g, dict) else {},
        )

    # Fallback to base annotation
    return Annotation(**base_kwargs)  # type: ignore[arg-type]


def _list_str_opt(v: Any) -> Optional[List[str]]:
    if v is None:
        return None
    if isinstance(v, list):
        out: List[str] = []
        for x in v:
            if isinstance(x, str):
                out.append(x)
        return out
    return None


def _rgba_opt(v: Any) -> Optional[RGBA]:
    if not isinstance(v, (list, tuple)) or len(v) != 4:
        return None
    try:
        r, g, b, a = (int(v[0]), int(v[1]), int(v[2]), int(v[3]))
        return (r, g, b, a)
    except Exception:
        return None


def _float_opt(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        return None


def _int_opt(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(v)
    except Exception:
        return None


def _pt_int2_opt(v: Any) -> Optional[Tuple[int, int]]:
    if not isinstance(v, (list, tuple)) or len(v) < 2:
        return None
    try:
        return (int(v[0]), int(v[1]))
    except Exception:
        return None
