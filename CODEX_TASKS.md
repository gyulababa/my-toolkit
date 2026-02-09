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

- [ ] ID=T0117 STATUS=TODO TYPE=refactor SCOPE=services/vision/catalog_seed.py VERIFY="pytest -q" DESC="Move repo-layout-dependent seed loader out of services and make seeding accept explicit helpers_root if kept reusable"
- [ ] ID=T0118 STATUS=TODO TYPE=refactor SCOPE=preview_vision/config_io.py VERIFY="pytest -q" DESC="Make preview_vision the sole owner of config IO wiring and pass built sources/config into services via injection"
- [ ] ID=T0119 STATUS=TODO TYPE=doc SCOPE=HELPERS_API.md VERIFY="pytest -q" DESC="Document layering rule that services must not import apps and GUI adapters must live outside services"
- [ ] ID=T0120 STATUS=TODO TYPE=doc SCOPE=services/vision/dpg_texture_pool.py VERIFY="pytest -q" DESC="Document TextureRef lifetime and resize retag behavior to prevent stale texture tag caching"
- [ ] ID=T0121 STATUS=TODO TYPE=chore SCOPE=services/vision/persist_impl.py VERIFY="pytest -q" DESC="Remove obsolete contentReference artifacts and normalize module comments"


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

