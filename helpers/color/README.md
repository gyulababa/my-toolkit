<!-- helpers/color/README.md -->
# helpers/color

## Purpose
UI-agnostic color helpers for small projects and internal tools:
- compact RGB value type
- RGB ↔ HSV conversion
- simple blending and luminance heuristics
- practical accent/variant generation
- parsing common user/CLI color formats

## Belongs here
- Lightweight color math and heuristics (not standards-grade)
- Parsing and normalization of simple RGB formats
- Generating UI-friendly “variants” from an anchor color

## Does not belong here
- WCAG/contrast compliance enforcement
- CSS parsing, named colors, theming engines
- Gamma-correct rendering pipelines
- Backend bindings (Qt/HTML/etc.)

## Public API (flat list)
### Types
- `ColorRGB`

### Functions
- `normalize_rgb(c) -> ColorRGB`
- `rgb_to_hsv(c) -> (h, s, v)`
- `hsv_to_rgb(h, s, v) -> ColorRGB`
- `blend_rgb(a, b, t) -> ColorRGB`
- `relative_luminance(c) -> float`
- `auto_fg_color(bg, threshold=0.5) -> ColorRGB`
- `opposite_hue_color(c) -> ColorRGB`
- `opposite_contrast_color(c) -> ColorRGB`
- `inverted_rgb(c) -> ColorRGB`
- `accent_low(c) -> ColorRGB`
- `accent_strong(c) -> ColorRGB`
- `variants_from_anchor(anchor, ...) -> (low, mid, high)`
- `fg_variants(bg) -> (primary_fg, secondary_fg)`
- `parse_color_rgb(s) -> ColorRGB`
