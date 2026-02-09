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
