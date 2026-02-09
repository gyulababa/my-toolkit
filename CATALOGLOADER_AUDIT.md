# Catalogloader Usage Audit

Date: 2026-02-09

## Allowed usages
- `helpers/catalogloader/*`
- `tests/test_catalog_and_catalogloader.py`
- Documentation references in `AGENTS.md`, `RUN_CODEX_REFACTOR.md`, `CODEX_TASKS.md`

## Non-test usages to migrate
- `services/tags_service.py`
- `services/vision/annotations_service.py`
- `services/vision/layers_service.py`
- `helpers/vision/config/defaults.py`
- `helpers/persist/persisted_catalog_loader.py`
- `helpers/zones/serde.py` (optional import)

