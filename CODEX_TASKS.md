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

- [ ] ID=T0190 STATUS=TODO TYPE=refactor SCOPE=app/adapters/dearpygui/panels/register_default_panels.py VERIFY="pytest -q" DESC="Review register_default_panels for correctness, layering, and imports; update parallel README in folder if needed"
- [ ] ID=T0191 STATUS=TODO TYPE=refactor SCOPE=app/adapters/dearpygui/ui/bootstrap.py VERIFY="pytest -q" DESC="Review DearPyGui UI bootstrap for correctness, layering, and imports; update parallel README in folder if needed"
- [ ] ID=T0192 STATUS=TODO TYPE=refactor SCOPE=helpers/toolkits/ui/runtime/autosave.py VERIFY="pytest -q" DESC="Review runtime autosave for correctness, layering, and imports; update parallel README in folder if needed"
- [ ] ID=T0193 STATUS=TODO TYPE=refactor SCOPE=pyproject.toml,my_toolkit/*,helpers/*,services/* VERIFY="pytest -q" DESC="Create my_toolkit/ import root and add compatibility shims for helpers/ and services/; update pyproject package discovery to include my_toolkit* and services*"
- [ ] ID=T0194 STATUS=TODO TYPE=refactor SCOPE=app/*,toolkit_adapters/*,my_toolkit/* VERIFY="pytest -q" DESC="Move/rename toolkit app/ package to my_toolkit/toolkit_adapters/ (avoid top-level app namespace); add minimal compat shim if needed"
- [ ] ID=T0195 STATUS=TODO TYPE=refactor SCOPE=preview_vision/*,examples/preview_vision/* VERIFY="pytest -q" DESC="Move preview_vision/ to repo examples/preview_vision/ (not packaged) and update any references/entrypoints accordingly"
- [ ] ID=T0196 STATUS=TODO TYPE=refactor SCOPE=helpers/lighting/*,helpers/led_pixels/*,my_toolkit/helpers/* VERIFY="pytest -q" DESC="Rename helpers/lighting to my_toolkit/helpers/led_pixels (LED pixel strips, not monitor pixels); add compat import shim if required"
- [ ] ID=T0197 STATUS=TODO TYPE=refactor SCOPE=. VERIFY="pytest -q" DESC="Update imports, tests, and docs to new namespaces (my_toolkit.*, toolkit_adapters.*, led_pixels); ensure pytest -q passes and docs reflect new layout"

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

