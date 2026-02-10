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

- [ ] ID=T0159 STATUS=TODO TYPE=refactor SCOPE=app/ VERIFY="pytest -q" DESC="Audit app folder modules for incorrect imports and fix paths to respect layering and package structure"

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

