# RUN_CODEX_REFACTOR.md — Codex Execution Driver (Task Registry Mode)

## Control Chain

Authority order:
1) RUN_CODEX_REFACTOR.md — execution driver
2) AGENTS.md — rules + architecture
3) CODEX_TASKS.md — task registry

AGENTS.md overrides all.

---

## Purpose

Run Codex in guardrail/enforcement mode using a machine-checkable task registry.

Canonical persistence API:
- helpers.persist = canonical
- helpers.catalogloader = deprecated facade

Do NOT execute roadmap items in CODEX_FUTURE_PLANS.md unless explicitly instructed.

---

## One-Line Codex Prompt (VS Code)

Follow RUN_CODEX_REFACTOR.md exactly. Obey AGENTS.md. Execute tasks from CODEX_TASKS.md in ID order. For each task: make one focused commit, run `pytest -q`, then mark the task line STATUS=DONE with COMMIT=<sha> DATE=<YYYY-MM-DD>. Do not execute CODEX_FUTURE_PLANS.md.

---

## Execution Notes

- Tasks are executed in order, one per commit.
- Only update the STATUS line fields; do not rewrite task descriptions.
- Guardrail: helpers/* must not import helpers.catalogloader outside helpers/catalogloader/* (enforced by tests).
- Guardrail: persistence markers (index.json, active_id, next_int, persist_root) confined to helpers/persist/* and helpers/catalogloader/*.
- Guardrail: helpers/* forbidden imports (UI frameworks, services, requests, subprocess) enforced by tests.

If a task cannot be completed:
- set STATUS=SKIP in CODEX_TASKS.md
- keep checkbox unchecked
- include reason in final summary

If implementing a new guardrail test would fail due to known migration backlog, either:
- migrate the backlog first (preferred), or
- scope the guardrail to helpers/* only (allowed), and keep backlog tracked.

---

## Final Summary Requirements

- list executed task IDs
- commits created
- pytest results
- any tasks skipped and rationale
