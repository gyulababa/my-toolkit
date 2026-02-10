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

- [ ] ID=T0194 STATUS=TODO TYPE=refactor SCOPE=app/*,toolkit_adapters/*,my_toolkit/* VERIFY="pytest -q" DESC="Move toolkit app package to my_toolkit/toolkit_adapters and add minimal compatibility shim for old imports"
- [ ] ID=T0195 STATUS=TODO TYPE=refactor SCOPE=preview_vision/*,examples/preview_vision/* VERIFY="pytest -q" DESC="Move preview_vision to examples/preview_vision and update references and entrypoints"
- [ ] ID=T0196 STATUS=TODO TYPE=refactor SCOPE=helpers/lighting/*,helpers/led_pixels/*,my_toolkit/helpers/* VERIFY="pytest -q" DESC="Rename helpers lighting to my_toolkit.helpers.led_pixels and add compatibility import shim if required"
- [ ] ID=T0197 STATUS=TODO TYPE=refactor SCOPE=. VERIFY="pytest -q" DESC="Update imports tests and docs to new namespaces my_toolkit toolkit_adapters and led_pixels and ensure tests pass"
- [ ] ID=T0198 STATUS=TODO TYPE=chore SCOPE=.gitignore VERIFY="pytest -q" DESC="Add ignore rule for my_toolkit.egg-info to keep editable install artifacts out of version control"
- [ ] ID=T0199 STATUS=TODO TYPE=refactor SCOPE=helpers/toolkits/ui/spec/models.py VERIFY="pytest -q" DESC="Resolve unexpected modification to spec models by reverting or accepting with reviewed imports and README updates"
- [ ] ID=T0200 STATUS=TODO TYPE=refactor SCOPE=**/__init__.py VERIFY="pytest -q" DESC="Audit added or modified __init__ modules for correct exports imports and layering compliance"


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

