# Helpers Package — Public API vs Internal Helpers

The `helpers/` package is intentionally layered.

Not everything inside it is meant to be used everywhere.

This document defines what is considered stable **public API** versus what exists primarily to support other helpers or infrastructure code.

## 1) Public API Helpers (Stable, Intended for Broad Use)

These helpers are safe to import and use from:

- UI code
- Services
- CLI tools
- Tests
- Core / domain logic

They are:

- Explicitly exported in `helpers/__init__.py` (and/or package-level `__init__.py`)
- Semantically stable
- Designed for readability and reuse

---

## Filesystem & IO (Public)

Module: `helpers.fs_utils`

Use when interacting with the filesystem in any layer.

Helper | Purpose
---|---
ensure_dir | Create directories safely
ls | List files with glob + recursion
find_upwards | Discover project roots
path_is_within | Prevent directory traversal
read_text, write_text | Text file IO
atomic_write_text | Safe config/state writes
read_bytes, write_bytes | Binary IO
read_json, write_json | JSON helpers
atomic_write_json | Atomic JSON persistence

Status: Public, stable

---

## Math (Public)

Modules:
- `helpers.math.basic`

Used across UI layout, animation, normalization, and logic.

Helper | Purpose
---|---
clamp, lerp, remap | Numeric normalization
smoothstep | Eased transitions
wrap_index | Circular indexing

Status: Public, stable

---

## Geometry (Public)

Modules:
- `helpers.geometry` (package entry point)
- `helpers.geometry.rect` (implementation)

Used across UI layout, selection rectangles, image/capture mapping, preview sizing.

Helper | Purpose
---|---
RectF | Float rectangle abstraction
fit_aspect | Aspect-preserving scaling (contain/cover)
clamp_rect_to_bounds | Keep RectF inside bounds
normalize_xyxy | Normalize (x0,y0,x1,y1) ordering
xyxy_is_valid | Min-size validity checks
clamp_xyxy_to_bounds | Clamp corners independently
clamp_xyxy_preserve_size | Clamp by shifting rect (preserve size)
xyxy_px_to_norm / xyxy_norm_to_px | Pixel ↔ normalized conversion

Status: Public, stable

---

## Validation (Public)

Modules:
- `helpers.validation.basic`
- `helpers.validation.time`

Used for config parsing, schema validation, CLI input validation.

### basic.py (Public)

Helper | Purpose
---|---
ValidationError | Unified validation error type
ensure_* | Scalar validation helpers (value + path)
require_* | Mapping validation helpers (mapping + key + path)
ensure_one_of / require_one_of | Enum validation
ensure_unique / require_unique | Uniqueness checks
ensure_ip / require_ip | IP address validation (scalar + mapping)

Status: Public, stable

### time.py (Public)

Helper | Purpose
---|---
parse_time_of_day | Parse "HH:MM[:SS]"
resolve_time_like | Normalize datetime/unix/time-of-day inputs
ensure_end_after_start | Midnight guard utility
ensure_tz | Ensure tz-awareness

Status: Public, stable

---

## Zones (Public)

Modules:
- `helpers.zones.schema`
- `helpers.zones.editor`
- `helpers.zones.serde`

Agnostic “Zones Preset Library” model intended for:
- OCR zones
- UI overlays
- capture crops
- any spatial consumer configs (via `consumers.{key}`)

Key concepts:
- `schema_version`
- `presets.{preset_id}.zones.{zone_key}`
- `geometry` is explicit (`rect_px`, `rect_norm`)
- `consumers` is an open-ended dict of dicts (opaque to the zones layer)

Status: Public, stable (schema_versioned)

---

## History / Operations (Public)

Modules:
- `helpers.history.*`

A universal operation/history foundation for:
- undo/redo
- batching
- coalescing (drag operations)
- replayable edits

Status: Public, stable

---

## 2) Internal Helpers (Infrastructure / Support)

These helpers exist to support public helpers or provide low-level infrastructure.

They may:
- change more frequently
- be reorganized or inlined
- have stricter assumptions

They are not recommended for direct use in UI or feature code unless you know why you need them.

### Byte / Frame Utilities (Semi-internal)

Module: `helpers.bytes_conv`

Purpose:
- Packed RGB frame construction
- LUT/gamma transforms
- LED backend support

These are:
- low-level
- performance-oriented
- backend-specific

Safe to use inside rendering / driver layers, but avoid in domain logic.

---

## 3) Import Rules (Recommended)

### Service/App Layering (Mandatory)

Services must not import toolkit adapter modules.

GUI adapters must live outside `services/` (use `my_toolkit/toolkit_adapters/adapters/...`).

Preferred (Public API):

```python
from helpers.geometry import fit_aspect, RectF
from helpers.validation import ValidationError, ensure_str
from helpers.zones.editor import ZonesEditor
Allowed (Infrastructure layers only):


from helpers.bytes_conv import apply_gamma_u8
Avoid:

importing underscore-prefixed internals

importing from “semi-internal” modules in business logic

4) Stability Guarantees
Category	Stability
Public helpers	High
Semi-internal helpers	Medium
Internal constants	None

Public helpers aim for backward compatibility.
Internal helpers may change when architecture evolves.


---

### One small recommendation (optional, but consistent)
If you are now relying on package exports (e.g., `from helpers.geometry import ...`, `from helpers.validation import ...`), ensure you have:

- `helpers/geometry/__init__.py` exporting rect helpers
- `helpers/validation/__init__.py` exporting basic/time helpers

This matches the “Public API is exported” claim in the doc.

If you want, I can also rewrite your root `helpers/__init__.py` to re-export the intended “public surface” (and keep everything else importable by full path).
::contentReference[oaicite:4]{index=4}

