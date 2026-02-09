<!-- helpers/math/README.md -->
# helpers/math

## Purpose
Small numeric primitives used across the helpers package:
- clamps
- interpolation and remapping
- safe division
- rounding/wrapping utilities
- small easing functions

## Belongs here
- “Leaf” math utilities with no domain meaning
- Helpers intended to be reused by many other subpackages (color, geometry, etc.)

## Does not belong here
- Geometry types and operations → `helpers/geometry`
- Color conversions/heuristics → `helpers/color`
- Statistics, linear algebra, heavy math modules

## Public API (flat list)
- `clamp(v, lo, hi) -> float`
- `clamp01(v) -> float`
- `clamp8(v) -> int`
- `clamp_int(v, lo, hi) -> int`
- `lerp(a, b, t) -> float`
- `inv_lerp(a, b, v) -> float`
- `remap(in_a, in_b, out_a, out_b, v) -> float`
- `safe_div(n, d, default=0.0) -> float`
- `round_int(v) -> int`
- `wrap_index(i, n) -> int`
- `smoothstep(edge0, edge1, x) -> float`
