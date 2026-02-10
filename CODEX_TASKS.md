# CODEX_TASKS.md — Task Registry (Guardrail Mode)

Baseline:
- helpers.persist = canonical persistence layer (implemented)
- helpers.catalogloader = deprecated facade (implemented)
- migration phases are DONE

This file is the ONLY automatic execution source for Codex tasks.
Roadmap items live in CODEX_FUTURE_PLANS.md and are NOT executed unless explicitly copied here.

---

## How Codex must operate

1) Execute tasks in ID order (T0001..).
2) For each task:
   - make a single focused commit
   - run the VERIFY command
   - mark task as DONE only if VERIFY passes
   - do not amend the task commit for registry updates
3) After completing at least one task:
   - update AGENTS.md / RUN_CODEX_REFACTOR.md if needed
   - create a registry-update commit to copy all STATUS=DONE tasks (with COMMIT=<task_sha> and DATE) verbatim into CODEX_TASK_HISTORY.md and remove them from CODEX_TASKS.md (append-only history; mandatory)
4) Tasks must NOT be merged or reordered.
5) Exactly one registry task per commit.

---

## Task Registry

- [ ] =T0149 STATUS=TODO TYPE=test SCOPE=tests/lighting/test_pixel_buffer_editor_history.py VERIFY="pytest -q" DESC="Add tests verifying PixelBufferEditor uses History ops when history.doc is bound and supports undo redo of edits"

- [ ] =T0150 STATUS=TODO TYPE=refactor SCOPE=helpers/strip_map.py VERIFY="pytest -q" DESC="Refactor strip_map naming and docs to emphasize discrete axis utility and prepare compatibility aliasing for future renames"

- [ ] =T0151 STATUS=TODO TYPE=refactor SCOPE=helpers/strip_preview_ascii.py VERIFY="pytest -q" DESC="Refactor strip_preview_ascii docstrings to clarify non LED usage while keeping backward compatible signatures"

- [ ] =T0152 STATUS=TODO TYPE=doc SCOPE=CODEX_PIXEL_STRIPS.md VERIFY="pytest -q" DESC="Document pixel strips schema- [ ]  and naming conventions endpoint semantics and PixelBufferEditor API contracts"

- [ ] =T0153 STATUS=TODO TYPE=feat SCOPE=helpers/lighting/init.py VERIFY="pytest -q" DESC="Expose lighting public API exports for PixelBufferEditor and pixel strip model types with stable import paths"

- [ ] =T0154 STATUS=TODO TYPE=chore SCOPE=tests/lighting VERIFY="pytest -q" DESC="Add lighting test package scaffolding and ensure pytest discovery configuration"

- [ ] =T0155 STATUS=TODO TYPE=feat SCOPE=helpers/lighting/pixel_strips_validators.py VERIFY="pytest -q" DESC="Add validators for pixel strip raw docs covering schema version- [ ] s uniqueness pixel count match and endpoint fields"

- [ ] =T0156 STATUS=TODO TYPE=test SCOPE=tests/lighting/test_pixel_strips_validators.py VERIFY="pytest -q" DESC="Add tests for pixel strip validators including invalid RGB triplets brightness bounds endpoint parsing and duplicate- [ ] s"
---

## Completion rule

When a task is completed, update its line:
- set STATUS=DONE
- change checkbox to [x]
- append COMMIT=<sha> DATE=<YYYY-MM-DD>

---

## Control Doc Sync (Mandatory)

If any task changes architecture rules, workflow, or guardrails:

Codex MUST update:
- AGENTS.md
- RUN_CODEX_REFACTOR.md
- CODEX_TASKS.md

in the same run.

