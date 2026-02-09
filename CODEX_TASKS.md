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
3) After completing at least one task:
   - update AGENTS.md / RUN_CODEX_REFACTOR.md if needed
   - prune only tasks with STATUS=DONE (optional; preferred to keep history)
4) Tasks must NOT be merged or reordered.
5) Exactly one registry task per commit.

---

## Task Registry

- [x] ID=T0001 STATUS=DONE TYPE=test SCOPE=tests/ VERIFY="pytest -q" DESC="Add architecture import guard: fail if helpers.catalogloader is imported anywhere under helpers/* except helpers/catalogloader/*; allow tests/*; allow services/* (migration backlog tracked in CATALOGLOADER_AUDIT.md)" COMMIT=748a568 DATE=2026-02-09
- [x] ID=T0002 STATUS=DONE TYPE=test SCOPE=tests/ VERIFY="pytest -q" DESC="Add persist boundary guard test: fail if persistence markers (index.json, active_id, next_int, persist_root /) appear outside helpers/persist/* and helpers/catalogloader/*" COMMIT=e761b60 DATE=2026-02-09
- [x] ID=T0003 STATUS=DONE TYPE=test SCOPE=tests/ VERIFY="pytest -q" DESC="Add facade deprecation warning tests: ensure importing/constructing catalogloader facade emits DeprecationWarning" COMMIT=c6b1e7f DATE=2026-02-09
- [x] ID=T0004 STATUS=DONE TYPE=refactor SCOPE=helpers/persist/* VERIFY="pytest -q" DESC="Add missing type hints in helpers/persist (annotations only, no behavior changes)" COMMIT=759ad91 DATE=2026-02-09
- [x] ID=T0005 STATUS=DONE TYPE=test SCOPE=tests/ VERIFY="pytest -q" DESC="Add persist roundtrip test: persist -> load -> equality, using temp dir" COMMIT=064b26b DATE=2026-02-09
- [ ] ID=T0100 STATUS=TODO TYPE=refactor SCOPE=services/ VERIFY="pytest -q" DESC="Migrate known non-test catalogloader imports listed in CATALOGLOADER_AUDIT.md to helpers.persist equivalents (mechanical import-only refactor; keep behavior)"

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

