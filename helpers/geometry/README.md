<!-- helpers/geometry/README.md -->
# helpers/geometry

## Purpose
UI-agnostic geometry primitives and coordinate helpers:
- immutable float rectangles (`RectF`)
- aspect fit helpers (“contain/cover”)
- XYXY utilities (normalize/validate/clamp)
- pixel ↔ normalized coordinate conversions

## Belongs here
- Pure geometry math and primitives
- Coordinate conversions and clamping
- Aspect-preserving fit calculations

## Does not belong here
- Rendering (drawing, painters, widgets)
- Hit-testing against UI frameworks
- Domain meaning (ROI semantics, selection rules, etc.)

## Public API (flat list)
### Types
- `RectF`

### Functions
- `clamp_rect_to_bounds(r, bounds) -> RectF`
- `fit_aspect(src_w, src_h, dst_w, dst_h, mode="contain"|"cover") -> (w, h)`
- `fit_aspect_rect(src_w, src_h, dst_rect, mode="contain"|"cover", align_x=0..1, align_y=0..1) -> RectF`
- `normalize_xyxy(x0, y0, x1, y1) -> (x0, y0, x1, y1)`
- `xyxy_is_valid(x0, y0, x1, y1) -> bool`
- `clamp_xyxy_to_bounds(x0, y0, x1, y1, w, h) -> (x0, y0, x1, y1)`
- `clamp_xyxy_preserve_size(x0, y0, x1, y1, w, h) -> (x0, y0, x1, y1)`
- `xyxy_px_to_norm(x0, y0, x1, y1, w, h) -> (x0, y0, x1, y1)`
- `xyxy_norm_to_px(x0, y0, x1, y1, w, h, rounding="floor"|"round"|"ceil") -> (x0, y0, x1, y1)`
