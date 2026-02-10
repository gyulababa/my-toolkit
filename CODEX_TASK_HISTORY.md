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
- [x] =T0008 STATUS=DONE TYPE=chore SCOPE=helpers/lighting/,ops_refresh.py VERIFY="pytest -q" DESC="Review untracked helpers/lighting/ and ops_refresh.py: summarize intent, determine correct layer/ownership, and either integrate (add init/typing/tests if needed) or remove/ignore; commit only if within intended architecture" COMMIT=29a2de3 DATE=2026-02-10
- [x] =T0144 STATUS=DONE TYPE=feat SCOPE=helpers/lighting/pixel_strips_model.py VERIFY="pytest -q" DESC="Add pixel strip core model (PixelColorRGB, StripType, Endpoint) and raw seed helpers for persisted docs" COMMIT=7f78fc0 DATE=2026-02-10
- [x] =T0145 STATUS=DONE TYPE=feat SCOPE=helpers/lighting/pixel_buffer_editor.py VERIFY="pytest -q" DESC="Implement PixelBufferEditor with create/delete/metadata/pixel edit ops using optional History push_* integration" COMMIT=ccabf9b DATE=2026-02-10
- [x] =T0146 STATUS=DONE TYPE=feat SCOPE=helpers/lighting/pixel_strip_ascii_debug.py VERIFY="pytest -q" DESC="Add ASCII debug preview helpers that reuse FixedStrip and strip_preview_ascii for quick headless visualization" COMMIT=2ae85b3 DATE=2026-02-10
- [x] =T0147 STATUS=DONE TYPE=test SCOPE=tests/lighting/test_pixel_buffer_editor_basic.py VERIFY="pytest -q" DESC="Add tests for create/delete strip, set_pixel, fill, set_range, and render_rgb_bytes brightness application" COMMIT=2e0230b DATE=2026-02-10
- [x] =T0148 STATUS=DONE TYPE=test SCOPE=tests/lighting/test_pixel_buffer_editor_resize.py VERIFY="pytest -q" DESC="Add tests for resize_pixels increase/decrease preserving prefix and enforcing pixel_count and pixels length invariants" COMMIT=2d82bee DATE=2026-02-10
- [x] =T0149 STATUS=DONE TYPE=test SCOPE=tests/lighting/test_pixel_buffer_editor_history.py VERIFY="pytest -q" DESC="Add tests verifying PixelBufferEditor uses History ops when history.doc is bound and supports undo redo of edits" COMMIT=7b8e685 DATE=2026-02-10
- [x] =T0150 STATUS=DONE TYPE=refactor SCOPE=helpers/strip_map.py VERIFY="pytest -q" DESC="Refactor strip_map naming and docs to emphasize discrete axis utility and prepare compatibility aliasing for future renames" COMMIT=d25e407 DATE=2026-02-10
- [x] =T0151 STATUS=DONE TYPE=refactor SCOPE=helpers/strip_preview_ascii.py VERIFY="pytest -q" DESC="Refactor strip_preview_ascii docstrings to clarify non LED usage while keeping backward compatible signatures" COMMIT=5d82c30 DATE=2026-02-10
- [x] =T0152 STATUS=DONE TYPE=doc SCOPE=CODEX_PIXEL_STRIPS.md VERIFY="pytest -q" DESC="Document pixel strips schema- [ ]  and naming conventions endpoint semantics and PixelBufferEditor API contracts" COMMIT=ce80add DATE=2026-02-10
- [x] =T0153 STATUS=DONE TYPE=feat SCOPE=helpers/lighting/init.py VERIFY="pytest -q" DESC="Expose lighting public API exports for PixelBufferEditor and pixel strip model types with stable import paths" COMMIT=4bb1b09 DATE=2026-02-10
- [x] =T0154 STATUS=DONE TYPE=chore SCOPE=tests/lighting VERIFY="pytest -q" DESC="Add lighting test package scaffolding and ensure pytest discovery configuration" COMMIT=6ba570f DATE=2026-02-10
- [x] =T0155 STATUS=DONE TYPE=feat SCOPE=helpers/lighting/pixel_strips_validators.py VERIFY="pytest -q" DESC="Add validators for pixel strip raw docs covering schema version- [ ] s uniqueness pixel count match and endpoint fields" COMMIT=1b2cc93 DATE=2026-02-10
- [x] =T0156 STATUS=DONE TYPE=test SCOPE=tests/lighting/test_pixel_strips_validators.py VERIFY="pytest -q" DESC="Add tests for pixel strip validators including invalid RGB triplets brightness bounds endpoint parsing and duplicate- [ ] s" COMMIT=8b4bc82 DATE=2026-02-10
- [x] ID=T0157 STATUS=DONE TYPE=chore SCOPE=pyproject.toml VERIFY="pytest -q" DESC="Ensure toolkit is installable as package name my-toolkit with proper project metadata and editable install support via pip install -e" COMMIT=8f36fa1 DATE=2026-02-10
- [x] ID=T0158 STATUS=DONE TYPE=chore SCOPE=**/*.py VERIFY="pytest -q" DESC="Scan all python source files and add first-line path comment like '# helpers/bytes_conv.py' where missing without altering logic" COMMIT=1a3c8d3 DATE=2026-02-10
- [x] ID=T0159 STATUS=DONE TYPE=refactor SCOPE=app/ VERIFY="pytest -q" DESC="Audit app folder modules for incorrect imports and fix paths to respect layering and package structure" COMMIT=c923af4 DATE=2026-02-10
- [x] ID=T0160 STATUS=DONE TYPE=doc SCOPE=helpers/ VERIFY="pytest -q" DESC="Audit helpers subfolders lighting, server, tags, toolkits, transforms, validation, vision, and zones for missing README files" COMMIT=8ed2ab5 DATE=2026-02-10
- [x] ID=T0161 STATUS=DONE TYPE=doc SCOPE=helpers/**/README.md VERIFY="pytest -q" DESC="Create README files for helpers lighting, server, tags, toolkits and its subfolders, transforms, validation, vision, and zones" COMMIT=24bdd3b DATE=2026-02-10
- [x] ID=T0162 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/spec/ VERIFY="pytest -q" DESC="Review helpers.toolkits.ui.spec package and align module structure, exports, and naming with toolkit layering rules" COMMIT=5f8d856 DATE=2026-02-10
- [x] ID=T0163 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/state/ VERIFY="pytest -q" DESC="Review helpers.toolkits.ui.state package and ensure models serde migrate and loader integrate cleanly with persisted loader patterns" COMMIT=e67ca6a DATE=2026-02-10
- [x] ID=T0164 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/runtime/ VERIFY="pytest -q" DESC="Review helpers.toolkits.ui.runtime package and ensure runtime layer is frontend-agnostic and depends only on helpers and toolkits" COMMIT=bea5572 DATE=2026-02-10
- [x] ID=T0165 STATUS=DONE TYPE=refactor SCOPE=services/ui/ VERIFY="pytest -q" DESC="Review services.ui layer and confirm it binds UI state to persisted domain and history without importing app adapters" COMMIT=29b3e59 DATE=2026-02-10
- [x] ID=T0166 STATUS=DONE TYPE=refactor SCOPE=app/adapters/dearpygui/ui/ VERIFY="pytest -q" DESC="Review DearPyGui UI adapter modules and ensure they depend only on services.ui and helpers.toolkits.ui layers" COMMIT=7b3bb55 DATE=2026-02-10
- [x] ID=T0167 STATUS=DONE TYPE=refactor SCOPE=helpers/configs/ui/ui_spec.json VERIFY="pytest -q" DESC="Validate ui_spec.json against UI spec models and update fields to match schema and validation rules" COMMIT=53dbbc5 DATE=2026-02-10
- [x] ID=T0168 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/** VERIFY="pytest -q" DESC="Audit and correct imports across helpers.toolkits.ui packages to use canonical package paths and avoid cross-layer violations" COMMIT=ff7f492 DATE=2026-02-10
- [x] ID=T0169 STATUS=DONE TYPE=refactor SCOPE=services/ui/** VERIFY="pytest -q" DESC="Audit and correct imports across services.ui modules to ensure no adapter or app layer imports leak inward" COMMIT=bac6b34 DATE=2026-02-10
- [x] ID=T0170 STATUS=DONE TYPE=refactor SCOPE=app/adapters/dearpygui/ui/** VERIFY="pytest -q" DESC="Audit and correct imports across DearPyGui UI adapter modules to match final package paths and runtime contracts" COMMIT=241fb54 DATE=2026-02-10
- [x] ID=T0171 STATUS=DONE TYPE=doc SCOPE=helpers/toolkits/ui/spec/README.md VERIFY="pytest -q" DESC="Create or update README for helpers.toolkits.ui.spec describing spec models serde validate and file-driven menu design" COMMIT=e456220 DATE=2026-02-10
- [x] ID=T0172 STATUS=DONE TYPE=doc SCOPE=helpers/toolkits/ui/state/README.md VERIFY="pytest -q" DESC="Create or update README for helpers.toolkits.ui.state covering state models defaults migration serde and loader" COMMIT=b52e5b1 DATE=2026-02-10
- [x] ID=T0173 STATUS=DONE TYPE=doc SCOPE=helpers/toolkits/ui/runtime/README.md VERIFY="pytest -q" DESC="Create or update README for helpers.toolkits.ui.runtime documenting session commands windows events and autosave" COMMIT=198ace9 DATE=2026-02-10
- [x] ID=T0174 STATUS=DONE TYPE=doc SCOPE=services/ui/README.md VERIFY="pytest -q" DESC="Create or update README for services.ui explaining UI state service responsibilities and layering boundaries" COMMIT=34917db DATE=2026-02-10
- [x] ID=T0175 STATUS=DONE TYPE=doc SCOPE=app/adapters/dearpygui/ui/README.md VERIFY="pytest -q" DESC="Create or update README for DearPyGui UI adapter layer covering host bootstrap menus and window manager" COMMIT=40b787d DATE=2026-02-10
- [x] ID=T0176 STATUS=DONE TYPE=refactor SCOPE=app/adapters/dearpygui/ui/dpg_menu_builder.py VERIFY="pytest -q" DESC="Recheck dpg_menu_builder for incorrect imports and contract mismatches with UI spec/runtime and update implementation accordingly" COMMIT=94b098f DATE=2026-02-10
- [x] ID=T0177 STATUS=DONE TYPE=doc SCOPE=app/adapters/dearpygui/ui/README.md VERIFY="pytest -q" DESC="Update README for app/adapters/dearpygui/ui to reflect current module roles, imports, and bootstrap/menu/window architecture" COMMIT=2486665 DATE=2026-02-10
- [x] ID=T0178 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/runtime/commands.py VERIFY="pytest -q" DESC="Review accidental addition in runtime commands module; accept or adjust imports/contract usage and document impacts if needed" COMMIT=e08d405 DATE=2026-02-10
- [x] ID=T0179 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/runtime/events.py VERIFY="pytest -q" DESC="Review accidental addition in runtime events module; accept or adjust imports/contract usage and document impacts if needed" COMMIT=349b3a6 DATE=2026-02-10
- [x] ID=T0180 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/spec/models.py VERIFY="pytest -q" DESC="Review accidental addition in ui spec models; accept or adjust imports/contract usage and document impacts if needed" COMMIT=5a3cda1 DATE=2026-02-10
- [x] ID=T0181 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/state/migrate.py VERIFY="pytest -q" DESC="Review accidental addition in ui state migrate helper; accept or adjust imports/contract usage and document impacts if needed" COMMIT=aee5a6e DATE=2026-02-10
- [x] ID=T0182 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/spec/models.py VERIFY="pytest -q" DESC="Review spec models for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=745517d DATE=2026-02-10
- [x] ID=T0183 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/spec/serde.py VERIFY="pytest -q" DESC="Review spec serde for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=2061f7c DATE=2026-02-10
- [x] ID=T0184 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/spec/validate.py VERIFY="pytest -q" DESC="Review spec validate for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=e59493e DATE=2026-02-10
- [x] ID=T0185 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/runtime/spec_resolve.py VERIFY="pytest -q" DESC="Review runtime spec_resolve for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=16ce142 DATE=2026-02-10
- [x] ID=T0186 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/runtime/menu_enrich.py VERIFY="pytest -q" DESC="Review runtime menu_enrich for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=25ef088 DATE=2026-02-10
- [x] ID=T0187 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/runtime/session.py VERIFY="pytest -q" DESC="Review runtime session for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=eea6b62 DATE=2026-02-10
- [x] ID=T0188 STATUS=DONE TYPE=refactor SCOPE=app/adapters/dearpygui/panels/log_panel.py VERIFY="pytest -q" DESC="Review log_panel for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=c5a0f8a DATE=2026-02-10
- [x] ID=T0189 STATUS=DONE TYPE=refactor SCOPE=app/adapters/dearpygui/panels/about_panel.py VERIFY="pytest -q" DESC="Review about_panel for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=c1e48ad DATE=2026-02-10
- [x] ID=T0190 STATUS=DONE TYPE=refactor SCOPE=app/adapters/dearpygui/panels/register_default_panels.py VERIFY="pytest -q" DESC="Review register_default_panels for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=9b22828 DATE=2026-02-10
- [x] ID=T0191 STATUS=DONE TYPE=refactor SCOPE=app/adapters/dearpygui/ui/bootstrap.py VERIFY="pytest -q" DESC="Review DearPyGui UI bootstrap for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=6e16af6 DATE=2026-02-10
- [x] ID=T0192 STATUS=DONE TYPE=refactor SCOPE=helpers/toolkits/ui/runtime/autosave.py VERIFY="pytest -q" DESC="Review runtime autosave for correctness, layering, and imports; update parallel README in folder if needed" COMMIT=07523e0 DATE=2026-02-10
- [x] ID=T0193 STATUS=DONE TYPE=refactor SCOPE=pyproject.toml,my_toolkit/*,helpers/*,services/* VERIFY="pytest -q" DESC="Create my_toolkit import root with helpers and services compatibility shims and update package discovery to include my_toolkit* and services*" COMMIT=9eac14f DATE=2026-02-10
- [x] ID=T0194 STATUS=DONE TYPE=refactor SCOPE=app/*,toolkit_adapters/*,my_toolkit/* VERIFY="pytest -q" DESC="Move toolkit app package to my_toolkit/toolkit_adapters and add minimal compatibility shim for old imports" COMMIT=6971228 DATE=2026-02-10
- [x] ID=T0195 STATUS=DONE TYPE=refactor SCOPE=preview_vision/*,examples/preview_vision/* VERIFY="pytest -q" DESC="Move preview_vision to examples/preview_vision and update references and entrypoints" COMMIT=21d0f8a DATE=2026-02-10
- [x] ID=T0196 STATUS=DONE TYPE=refactor SCOPE=helpers/lighting/*,helpers/led_pixels/*,my_toolkit/helpers/* VERIFY="pytest -q" DESC="Rename helpers lighting to my_toolkit.helpers.led_pixels and add compatibility import shim if required" COMMIT=b12e32c DATE=2026-02-10
- [x] ID=T0197 STATUS=DONE TYPE=refactor SCOPE=. VERIFY="pytest -q" DESC="Update imports tests and docs to new namespaces my_toolkit toolkit_adapters and led_pixels and ensure tests pass" COMMIT=f1ba5bc DATE=2026-02-10
- [x] ID=T0198 STATUS=DONE TYPE=chore SCOPE=.gitignore VERIFY="pytest -q" DESC="Add ignore rule for my_toolkit.egg-info to keep editable install artifacts out of version control" COMMIT=c92a173 DATE=2026-02-10
