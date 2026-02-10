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

- [ ] ID=T0166 STATUS=TODO TYPE=refactor SCOPE=app/adapters/dearpygui/ui/ VERIFY="pytest -q" DESC="Review DearPyGui UI adapter modules and ensure they depend only on services.ui and helpers.toolkits.ui layers"
- [ ] ID=T0167 STATUS=TODO TYPE=refactor SCOPE=helpers/configs/ui/ui_spec.json VERIFY="pytest -q" DESC="Validate ui_spec.json against UI spec models and update fields to match schema and validation rules"
- [ ] ID=T0168 STATUS=TODO TYPE=refactor SCOPE=helpers/toolkits/ui/** VERIFY="pytest -q" DESC="Audit and correct imports across helpers.toolkits.ui packages to use canonical package paths and avoid cross-layer violations"
- [ ] ID=T0169 STATUS=TODO TYPE=refactor SCOPE=services/ui/** VERIFY="pytest -q" DESC="Audit and correct imports across services.ui modules to ensure no adapter or app layer imports leak inward"
- [ ] ID=T0170 STATUS=TODO TYPE=refactor SCOPE=app/adapters/dearpygui/ui/** VERIFY="pytest -q" DESC="Audit and correct imports across DearPyGui UI adapter modules to match final package paths and runtime contracts"
- [ ] ID=T0171 STATUS=TODO TYPE=doc SCOPE=helpers/toolkits/ui/spec/README.md VERIFY="pytest -q" DESC="Create or update README for helpers.toolkits.ui.spec describing spec models serde validate and file-driven menu design"
- [ ] ID=T0172 STATUS=TODO TYPE=doc SCOPE=helpers/toolkits/ui/state/README.md VERIFY="pytest -q" DESC="Create or update README for helpers.toolkits.ui.state covering state models defaults migration serde and loader"
- [ ] ID=T0173 STATUS=TODO TYPE=doc SCOPE=helpers/toolkits/ui/runtime/README.md VERIFY="pytest -q" DESC="Create or update README for helpers.toolkits.ui.runtime documenting session commands windows events and autosave"
- [ ] ID=T0174 STATUS=TODO TYPE=doc SCOPE=services/ui/README.md VERIFY="pytest -q" DESC="Create or update README for services.ui explaining UI state service responsibilities and layering boundaries"
- [ ] ID=T0175 STATUS=TODO TYPE=doc SCOPE=app/adapters/dearpygui/ui/README.md VERIFY="pytest -q" DESC="Create or update README for DearPyGui UI adapter layer covering host bootstrap menus and window manager"

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

