# Mypy Incremental Plan

Goal: introduce static typing without blocking day-to-day development.

Phase 1 (now):
- Baseline config in `mypy.ini`
- `ignore_missing_imports = True`
- No strictness flags enabled globally

Phase 2 (helpers core):
- Enable `check_untyped_defs = True` for `helpers/persist/*`
- Add targeted `disallow_untyped_defs = True` for new modules only

Phase 3 (helpers expansion):
- Expand Phase 2 settings to `helpers/fs/*`, `helpers/validation/*`, `helpers/catalog/*`
- Reduce `ignore_missing_imports` where stubs exist

Phase 4 (services):
- Enable `check_untyped_defs = True` for `services/*` after helpers coverage improves
- Gate new service modules with `disallow_untyped_defs = True`

Phase 5 (tighten):
- Evaluate turning on `warn_return_any`
- Reduce per-module `ignore_errors`
