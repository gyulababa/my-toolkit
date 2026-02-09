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
   - if the commit is amended and hash changes, a second `git commit --amend --no-edit` is allowed solely to correct COMMIT=<sha> in registry/history task lines
3) After completing at least one task:
   - update AGENTS.md / RUN_CODEX_REFACTOR.md if needed
   - prune only tasks with STATUS=DONE (optional; preferred to keep history)
4) Tasks must NOT be merged or reordered.
5) Exactly one registry task per commit.

---

## Task Registry

- [x] ID=T0103 STATUS=DONE TYPE=doc SCOPE=CODEX_* VERIFY="pytest -q" DESC="Doc maintenance: remove completed items from CODEX_FUTURE_PLANS.md; create CODEX_TASK_HISTORY.md using the same registry line format; move all STATUS=DONE tasks from CODEX_TASKS.md into CODEX_TASK_HISTORY.md without rewriting their fields" COMMIT=9dade7d DATE=2026-02-09
- [x] ID=T0104 STATUS=DONE TYPE=doc SCOPE=AGENTS.md VERIFY="pytest -q" DESC="Update AGENTS.md: add Commit SHA Registry Rule section allowing exactly one git commit --amend --no-edit solely to inject COMMIT=<sha> into registry/history task lines" COMMIT=a3bc25a DATE=2026-02-09
- [x] ID=T0105 STATUS=DONE TYPE=doc SCOPE=AGENTS.md,CODEX_TASKS.md,RUN_CODEX_REFACTOR.md VERIFY="pytest -q" DESC="Adjust registry rules to allow one extra amend OR a post-commit registry update so COMMIT=<sha> matches final amended hash (fix mismatch like T0104 pre-amend vs final hash)" COMMIT=bb77427 DATE=2026-02-09
- [ ] ID=T0106 STATUS=TODO TYPE=doc SCOPE=CODEX_TASKS.md,CODEX_TASK_HISTORY.md,RUN_CODEX_REFACTOR.md VERIFY="pytest -q" DESC="Enforce DONE-task archival: define mandatory rule that after any run, all STATUS=DONE tasks are copied verbatim into CODEX_TASK_HISTORY.md and removed from CODEX_TASKS.md (append-only history), and update RUN to require it"


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

