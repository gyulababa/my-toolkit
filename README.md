my-toolkit

A reusable Python toolbox with a clear layering model:
- `helpers/` contains small, composable primitives.
- `services/` contains domain-level orchestration built on helpers.
- `tests/` mirrors helpers/services and verifies expected behavior.

The goal is portability: lift helpers/services into new projects without dragging in UI or app-specific glue.


Quick Start

1) Run tests

```bash
pytest -q
```

2) Browse the public API surface

See `HELPERS_API.md` for what is intended to be stable and widely reusable.


Repository Layout

```
my-toolkit/
|-- helpers/          # Pure, reusable building blocks (lowest level)
|-- services/         # Reusable orchestration / domain services (mid level)
|-- tests/            # Toolkit-level tests (mirror helpers + services)
|-- preview_vision/   # Local preview app (example usage)
|-- README.md
|-- HELPERS_API.md
`-- pyproject.toml
```


Design Principles

Layering rules
- `helpers` are primitives: small, testable, and safe to import anywhere.
- `services` compose helpers into workflows and domain logic.
- Apps import services; services import helpers; helpers never import services.

Helpers: what they are
- Pure logic or explicitly stateful but generic.
- No knowledge of UI, CLI, or app workflows.
- File IO only through explicit fs helpers.

Helpers: what they are not
- One-off scripts or app glue.
- UI widgets.
- Project-specific workflows.

Services: what they are
- Orchestration glue between helpers.
- Domain-level workflows.
- Reusable stateful application logic.

Services: what they are not
- UI widgets or CLI commands.
- One-off scripts.


Helpers Overview

Helpers are grouped by concern. Highlights include:
- `helpers/fs/`: filesystem primitives, atomic writes, JSON/text/bytes helpers.
- `helpers/validation/`: input hygiene and schema validation.
- `helpers/history/`: operation history, undo/redo primitives.
- `helpers/catalog/` and `helpers/persist/`: editable catalogs and persisted revisioning.
- `helpers/vision/`: frame buffers, sources, transforms, and driver abstractions.
- `helpers/zones/`: zone schema and serde helpers.

See `HELPERS_API.md` for stable public surface guidance.


Services Overview

Services build on helpers to provide reusable workflows. Examples:
- `services/vision/`: orchestration for capture, preview, and persistence.
- `services/domain/`: base domain service patterns.

Services are meant to be imported into apps or tooling with minimal glue.


Configuration and Templates

A convention is used for JSON configs and templates:
- `helpers/configs/<app_name>/` for default configs
- `helpers/templates/<app_name>/` for templates

The `helpers/catalogloader/` helpers standardize loading, validation, and persistence in these layouts.


CSV Cleaner Recipes

The CSV cleaner scripts use a CatalogLoader-backed recipes config at `scripts/CSVcleaner/recipes.json`.
Schema shape:
- `vars`: string map used for `${VAR}` expansion in default paths.
- `recipes`: list of recipe objects (`id`, `description`, `input_default`, `output_default`, `keep`, `rename`, `html_col`, `meta_cols`).
- `quickruns`: mapping of quickrun id to recipe id list (old list shape is still accepted).

Resolution rules:
- `${VAR}` placeholders expand from `vars`.
- Environment overrides take precedence via `OPS_<VAR>` (e.g. `OPS_DATA_DIR`).

Validation is performed via `CSVcleaner.recipes_catalog_loader.RECIPES_LOADER` before running recipes.
Quickrun results can be persisted by supplying `--persist-root` to `cleaner_runner.py`, which writes a run report under the `cleaning_runs` domain using `helpers.persist`.


Usage Examples

Load a JSON config safely:

```python
from helpers.fs import read_json_strict

cfg = read_json_strict("helpers/configs/vision/default.json", root_types=(dict,))
```

Atomic write of JSON state:

```python
from helpers.fs import atomic_write_json

atomic_write_json("state.json", {"version": 1, "items": []})
```

Create and use an editable catalog:

```python
from helpers.catalog import EditableCatalog

editable = EditableCatalog(raw={"schema_version": 1, "items": {}})
```


Testing

Tests are organized to mirror the `helpers/` and `services/` layout.

Run all tests:

```bash
pytest -q
```


Notes on Public API

`HELPERS_API.md` defines what is considered stable and safe to import broadly.
If you add new helpers, update that document to keep the public surface clear.


Contributing

If you add or change functionality:
- Add tests in `tests/` to match the helper/service location.
- Keep helpers small and composable.
- Avoid introducing UI or app-specific logic into helpers.


License

Internal toolkit (no external license specified).
