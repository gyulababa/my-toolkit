# CODEX_TASK_HISTORY.md — Completed Task Registry (Immutable Log)

Purpose:
This file stores COMPLETED tasks moved from CODEX_TASKS.md.

Format:
- Uses the SAME single-line registry format as CODEX_TASKS.md
- Lines must be copied verbatim when tasks are completed
- Do NOT rewrite, reflow, or rephrase task lines
- Only append — never edit past entries

Authority:
- This file is append-only history
- CODEX_TASKS.md remains the active task registry
- AGENTS.md registry format rules apply here as well

---

## How entries get here (Codex rule)

When a task in CODEX_TASKS.md reaches:

    STATUS=DONE
    checkbox = [x]
    COMMIT=<sha>
    DATE=<YYYY-MM-DD>

Codex must:

1) Copy the full task line here unchanged
2) Then remove it from CODEX_TASKS.md
3) Preserve field order and spacing exactly
4) Use a registry-update commit to record COMMIT=<task_sha> and DATE from the task commit; never amend the task commit for registry updates

---

## Completed Tasks

<!-- Codex appends completed registry lines below this marker -->
- [x] ID=T0001 STATUS=DONE TYPE=test SCOPE=tests/ VERIFY="pytest -q" DESC="Add architecture import guard: fail if helpers.catalogloader is imported anywhere under helpers/* except helpers/catalogloader/*; allow tests/*; allow services/* (migration backlog tracked in CATALOGLOADER_AUDIT.md)" COMMIT=748a568 DATE=2026-02-09
- [x] ID=T0002 STATUS=DONE TYPE=test SCOPE=tests/ VERIFY="pytest -q" DESC="Add persist boundary guard test: fail if persistence markers (index.json, active_id, next_int, persist_root /) appear outside helpers/persist/* and helpers/catalogloader/*" COMMIT=e761b60 DATE=2026-02-09
- [x] ID=T0003 STATUS=DONE TYPE=test SCOPE=tests/ VERIFY="pytest -q" DESC="Add facade deprecation warning tests: ensure importing/constructing catalogloader facade emits DeprecationWarning" COMMIT=c6b1e7f DATE=2026-02-09
- [x] ID=T0004 STATUS=DONE TYPE=refactor SCOPE=helpers/persist/* VERIFY="pytest -q" DESC="Add missing type hints in helpers/persist (annotations only, no behavior changes)" COMMIT=759ad91 DATE=2026-02-09
- [x] ID=T0005 STATUS=DONE TYPE=test SCOPE=tests/ VERIFY="pytest -q" DESC="Add persist roundtrip test: persist -> load -> equality, using temp dir" COMMIT=064b26b DATE=2026-02-09
- [x] ID=T0100 STATUS=DONE TYPE=refactor SCOPE=services/ VERIFY="pytest -q" DESC="Migrate known non-test catalogloader imports listed in CATALOGLOADER_AUDIT.md to helpers.persist equivalents (mechanical import-only refactor; keep behavior)" COMMIT=c0cab83 DATE=2026-02-09
- [x] ID=T0101 STATUS=DONE TYPE=test SCOPE=tests/ VERIFY="pytest -q" DESC="Expand architecture guard suite: enforce UI import bans and layer graph boundary checks (helpers/* frontend-agnostic)" COMMIT=d37774a DATE=2026-02-09
- [x] ID=T0102 STATUS=DONE TYPE=chore SCOPE=tooling/ VERIFY="pytest -q" DESC="Add mypy config and incremental strictness plan (no behavior changes)" COMMIT=1e90391 DATE=2026-02-09
- [x] ID=T0103 STATUS=DONE TYPE=doc SCOPE=CODEX_* VERIFY="pytest -q" DESC="Doc maintenance: remove completed items from CODEX_FUTURE_PLANS.md; create CODEX_TASK_HISTORY.md using the same registry line format; move all STATUS=DONE tasks from CODEX_TASKS.md into CODEX_TASK_HISTORY.md without rewriting their fields" COMMIT=9dade7d DATE=2026-02-09
- [x] ID=T0104 STATUS=DONE TYPE=doc SCOPE=AGENTS.md VERIFY="pytest -q" DESC="Update AGENTS.md: add Commit SHA Registry Rule section allowing exactly one git commit --amend --no-edit solely to inject COMMIT=<sha> into registry/history task lines" COMMIT=a3bc25a DATE=2026-02-09
- [x] ID=T0105 STATUS=DONE TYPE=doc SCOPE=AGENTS.md,CODEX_TASKS.md,RUN_CODEX_REFACTOR.md VERIFY="pytest -q" DESC="Adjust registry rules to allow one extra amend OR a post-commit registry update so COMMIT=<sha> matches final amended hash (fix mismatch like T0104 pre-amend vs final hash)" COMMIT=bb77427 DATE=2026-02-09
- [x] ID=T0106 STATUS=DONE TYPE=doc SCOPE=CODEX_TASKS.md,CODEX_TASK_HISTORY.md,RUN_CODEX_REFACTOR.md VERIFY="pytest -q" DESC="Enforce DONE-task archival: define mandatory rule that after any run, all STATUS=DONE tasks are copied verbatim into CODEX_TASK_HISTORY.md and removed from CODEX_TASKS.md (append-only history), and update RUN to require it" COMMIT=13eff11 DATE=2026-02-09
- [x] ID=T0107 STATUS=DONE TYPE=doc SCOPE=AGENTS.md,RUN_CODEX_REFACTOR.md,CODEX_TASKS.md,CODEX_TASK_HISTORY.md VERIFY="pytest -q" DESC="Fix self-referential COMMIT hash rule: stop using amend for registry updates; require separate post-task commit to record COMMIT=<task_sha> in history (no recursion), and update docs to define task commit vs registry-update commit" COMMIT=42471ef DATE=2026-02-09
- [x] ID=T0108 STATUS=DONE TYPE=fix SCOPE=services/vision/preview_session.py VERIFY="pytest -q" DESC="Remove services->preview_vision import by injecting config/source builder callables into VisionPreviewSession" COMMIT=6e73069 DATE=2026-02-09
- [x] ID=T0109 STATUS=DONE TYPE=refactor SCOPE=services/vision VERIFY="pytest -q" DESC="Introduce services.vision interfaces/types for FrameSource factory and config loader to keep preview app as wiring only" COMMIT=f734197 DATE=2026-02-09
- [x] ID=T0110 STATUS=DONE TYPE=refactor SCOPE=services/vision/dpg_* VERIFY="pytest -q" DESC="Move DearPyGui-specific modules out of services/vision into app/adapters/dearpygui/vision" COMMIT=4bbd763 DATE=2026-02-09
- [x] ID=T0111 STATUS=DONE TYPE=refactor SCOPE=services/vision/stage_surface.py VERIFY="pytest -q" DESC="Relocate StageSurface to app/adapters/dearpygui/vision and update all imports" COMMIT=fc885d7 DATE=2026-02-09
- [x] ID=T0112 STATUS=DONE TYPE=refactor SCOPE=services/vision/viewport_compositor.py VERIFY="pytest -q" DESC="Relocate ViewportCompositor to app/adapters/dearpygui/vision and update all imports" COMMIT=7fe63ff DATE=2026-02-09
- [x] ID=T0113 STATUS=DONE TYPE=fix SCOPE=helpers/vision/transforms.py VERIFY="pytest -q" DESC="Fix crop rect parameter contract mismatch by supporting xywh_norm or converting rect_norm [x,y,w,h] to xyxy before crop" COMMIT=3eb5f27 DATE=2026-02-09
- [x] ID=T0114 STATUS=DONE TYPE=test SCOPE=tests/vision/test_transforms_crop.py VERIFY="pytest -q" DESC="Add unit tests covering crop rect normalization for both rect_norm (xywh) and xyxy semantics" COMMIT=5437f16 DATE=2026-02-09
- [x] ID=T0115 STATUS=DONE TYPE=fix SCOPE=services/vision/layers_service.py VERIFY="pytest -q" DESC="Fix malformed import line(s) and ensure module imports cleanly without stray artifacts" COMMIT=84bdb5b DATE=2026-02-09
- [x] ID=T0116 STATUS=DONE TYPE=fix SCOPE=services/vision/annotations_service.py VERIFY="pytest -q" DESC="Fix malformed import line(s) and ensure module imports cleanly without stray artifacts" COMMIT=18e7dce DATE=2026-02-09
- [x] ID=T0117 STATUS=DONE TYPE=refactor SCOPE=services/vision/catalog_seed.py VERIFY="pytest -q" DESC="Move repo-layout-dependent seed loader out of services and make seeding accept explicit helpers_root if kept reusable" COMMIT=dc9423e DATE=2026-02-09
- [x] ID=T0118 STATUS=DONE TYPE=refactor SCOPE=preview_vision/config_io.py VERIFY="pytest -q" DESC="Make preview_vision the sole owner of config IO wiring and pass built sources/config into services via injection" COMMIT=ee275ea DATE=2026-02-09
- [x] ID=T0119 STATUS=DONE TYPE=doc SCOPE=HELPERS_API.md VERIFY="pytest -q" DESC="Document layering rule that services must not import apps and GUI adapters must live outside services" COMMIT=350c306 DATE=2026-02-09
- [x] ID=T0120 STATUS=DONE TYPE=doc SCOPE=services/vision/dpg_texture_pool.py VERIFY="pytest -q" DESC="Document TextureRef lifetime and resize retag behavior to prevent stale texture tag caching" COMMIT=b52ff65 DATE=2026-02-09
- [x] ID=T0121 STATUS=DONE TYPE=chore SCOPE=services/vision/persist_impl.py VERIFY="pytest -q" DESC="Remove obsolete contentReference artifacts and normalize module comments" COMMIT=31fd112 DATE=2026-02-09
 - [x] ID=T0122 STATUS=DONE TYPE=refactor SCOPE=cleaner_runner.py VERIFY="pytest -q" DESC="Replace ad-hoc recipes.json parsing with CatalogLoader-backed CleaningRecipesDoc + resolve step for env overrides and ${VAR} expansion" COMMIT=9773d53 DATE=2026-02-09
 - [x] ID=T0123 STATUS=DONE TYPE=feat SCOPE=scripts/CSVcleanerrecipes_schema.py VERIFY="pytest -q" DESC="Add typed CleaningRecipesDoc/Resolved model to represent recipe config and resolved defaults with validation" COMMIT=2ea0914 DATE=2026-02-09
 - [x] ID=T0124 STATUS=DONE TYPE=feat SCOPE=scripts/CSVcleanerrecipes_catalog_loader.py VERIFY="pytest -q" DESC="Implement CatalogLoader for cleaning recipes with validate/dump and back-compat parsing for old quickruns list shape" COMMIT=94d9cb2 DATE=2026-02-09
 - [x] ID=T0125 STATUS=DONE TYPE=test SCOPE=tests/scripts/CSVcleaner/test_recipes_loader.py VERIFY="pytest -q" DESC="Add tests for recipes schema validation, duplicate - [ ] IDs, unknown quickrun recipe refs, env override resolution, and ${VAR} expansion" COMMIT=b96d849 DATE=2026-02-09
 - [x] ID=T0126 STATUS=DONE TYPE=feat SCOPE=scripts/CSVcleanerrun_report.py VERIFY="pytest -q" DESC="Add persisted cleaning run report domain using PersistedCatalogLoader for quickrun results and reproducibility metadata" COMMIT=e199c95 DATE=2026-02-09
 - [x] ID=T0127 STATUS=DONE TYPE=refactor SCOPE=cleaner_runner.py VERIFY="pytest -q" DESC="Add optional persist_root arg and write run report revisions for quickruns via PersistedCatalogLoader when enabled" COMMIT=afb7aa6 DATE=2026-02-09
 - [x] ID=T0128 STATUS=DONE TYPE=doc SCOPE=README.md VERIFY="pytest -q" DESC="Document recipes.json schema, CatalogLoader-backed validation, env override rules, and optional persisted run reports" COMMIT=499e817 DATE=2026-02-09
 - [x] ID=T0129 STATUS=DONE TYPE=refactor SCOPE=clean_csv_generic.py VERIFY="pytest -q" DESC="Add optional sidecar metadata JSON writer (columns, rows, encoding, ragged) using CatalogLoader to standardize export provenance" COMMIT=f4a0798 DATE=2026-02-09
 - [x] ID=T0130 STATUS=DONE TYPE=test SCOPE=tests/scripts/CSVcleaner/test_clean_csv_sidecar.py VERIFY="pytest -q" DESC="Add tests verifying sidecar metadata content for normal parse and on_bad_lines=skip ragged parse paths" COMMIT=8110972 DATE=2026-02-09
 - [x] ID=T0131 STATUS=DONE TYPE=refactor SCOPE=app/adapters VERIFY="pytest -q" DESC="Introduce mid-level adapters package for CSV cleaning (config resolve, persist integration) to keep scripts thin and layering-compliant" COMMIT=e6b6e7a DATE=2026-02-09
- [x] ID=T0138 STATUS=DONE TYPE=fix SCOPE=helpers/zones/editor.py VERIFY="pytest -q" DESC="Fix undefined normalize_rect_px and clamp_rect_px by switching ZonesEditor.set_rect_px to helpers.transforms.imaging.crop/geometry helpers" COMMIT=d871f7b DATE=2026-02-09
- [x] ID=T0139 STATUS=DONE TYPE=refactor SCOPE=helpers/zones/editor.py VERIFY="pytest -q" DESC="Refactor ZonesEditor geometry normalization to call helpers.geometry.rect.normalize_xyxy and clamp_xyxy_to_bounds instead of local helpers" COMMIT=f01dd65 DATE=2026-02-09
- [x] ID=T0140 STATUS=DONE TYPE=refactor SCOPE=helpers/zones/editor.py VERIFY="pytest -q" DESC="Remove unused imports in ZonesEditor (normalize_xyxy, clamp_xyxy_preserve_size) after migrating to helpers.transforms.imaging.crop API" COMMIT=f561012 DATE=2026-02-09
- [x] ID=T0141 STATUS=DONE TYPE=refactor SCOPE=helpers/transforms/imaging/crop.py VERIFY="pytest -q" DESC="Add crop_rect_xywh_norm_np wrapper to support rect_norm [x,y,w,h] by converting to xyxy and delegating to crop_rect_norm_np" COMMIT=76f0a97 DATE=2026-02-09
- [x] ID=T0142 STATUS=DONE TYPE=test SCOPE=tests/transforms/imaging/test_crop_rect_norm.py VERIFY="pytest -q" DESC="Add tests for crop_rect_norm_np and new xywh wrapper including clamping, empty crop policy, and xywh-to-xyxy conversion" COMMIT=2d932bf DATE=2026-02-09
- [x] ID=T0143 STATUS=DONE TYPE=refactor SCOPE=helpers/zones/editor.py VERIFY="pytest -q" DESC="Add ZonesEditor helper to coalesce geometry drag updates using coalesce_key while keeping History patch paths stable" COMMIT=fee6f0b DATE=2026-02-09
- [x] =T0006 STATUS=DONE TYPE=chore SCOPE=CODEX_TASKS.md VERIFY="pytest -q" DESC="Review unexpected CODEX_TASKS.md modifications (show diff, classify as valid registry-only edit vs scope leak); revert if invalid, or normalize to registry rules without reflow" COMMIT=a530269 DATE=2026-02-10
- [x] =T0007 STATUS=DONE TYPE=chore SCOPE=app/sqlite/ VERIFY="pytest -q" DESC="Review untracked app/sqlite/ contents: summarize purpose, decide keep vs delete vs ignore; if keep, add minimal docs/README and ensure no large/derived artifacts are committed" COMMIT=0038c55 DATE=2026-02-10
