# CODEX_PIXEL_STRIPS.md

## Purpose
Pixel strips are stored as a simple, list-based document suitable for helpers.persist or other catalog-like stores.
The schema is optimized for History list operations and headless tooling.

## Document Shape
Top-level document (raw dict):
- `schema_name`: string, default `"pixel_strips"`
- `schema_version`: int, default `1`
- `strips`: list of strip records (see below)

Strip record (raw dict):
- `id`: string, stable strip identifier (unique within the document)
- `type`: string enum, values like `"wled"`, `"visualizer"`, `"other"`
- `pixel_count`: int, number of pixels in the strip
- `pixels`: list of RGB triplets, length must equal `pixel_count`
  - each triplet is `[r, g, b]` with `0..255` ints
- `master_brightness`: float in `[0.0, 1.0]`
  - applied at render time, pixels are stored at full values
- `names`: dict
  - `display`: string
  - `aliases`: list of strings
- `endpoint`: optional dict
  - `kind`: string (e.g. `"ddp"`, `"visualizer"`)
  - `host`: optional string
  - `port`: optional int
  - `path`: optional string
  - `meta`: optional dict for extra routing metadata
- `placement`: optional string, human-oriented location label

## Naming Conventions
- `strip_id` should be stable and unique across the document.
- `type` values are lower-case strings from `StripType`.
- `names.display` is the primary user-facing name.
- `names.aliases` should include user-entered shorthand or legacy names.

## Endpoint Semantics
- `endpoint.kind` defines the route type and determines how other fields are interpreted.
- `host` and `port` are for networked endpoints (e.g. DDP or other protocols).
- `path` is for logical or in-app endpoints (e.g. visualizers).
- `meta` can include protocol-specific extra info without changing the schema.

## PixelBufferEditor API Contracts
PixelBufferEditor operates on an object with a `raw` dict containing the schema above.

Core contracts:
- `create_strip(...)` appends a new strip and returns its id.
- `delete_strip(strip_id)` removes a strip by id.
- `set_display_name`, `set_aliases`, `set_strip_type`, `set_endpoint`, `set_placement`
  mutate the corresponding metadata fields.
- `set_master_brightness(strip_id, value)` clamps value into `[0.0, 1.0]`.
- `resize_pixels(strip_id, new_count, fill=...)` keeps the prefix and enforces
  `pixel_count` and `pixels` length to match.
- `set_pixel(strip_id, index, color)` updates a single pixel.
- `fill(strip_id, color)` updates all pixels.
- `set_range(strip_id, start, length, color)` updates a contiguous range.
- `render_rgb_bytes(strip_id)` returns packed RGB bytes with master brightness applied.
- `list_strip_ids()` and `find_strip_id_by_name(name)` are convenience lookups.

History integration:
- If `history` is provided and `history.doc` is bound to the same `raw` document,
  PixelBufferEditor uses History `push_*` ops.
- This enables undo/redo and batch grouping without changing the external API.
