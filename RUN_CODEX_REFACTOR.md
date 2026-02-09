# RUN_CODEX_REFACTOR.md — Codex Execution Driver

## Control Chain

Authority order:

1. RUN_CODEX_REFACTOR.md — execution driver
2. AGENTS.md — rules + architecture
3. CODEX_TASKS.md — phase plan

AGENTS.md overrides all.

---

## Purpose

Run Codex in enforcement mode:

- helpers.persist = canonical persistence API
- helpers.catalogloader = deprecated facade
- migrate imports
- add deprecation warnings
- enforce boundaries

Workflow is idempotent and audit-first.

---

## One-Line Codex Prompt (VS Code)

Paste into Codex:

Follow RUN_CODEX_REFACTOR.md exactly. Enforce helpers.persist as canonical persistence API, deprecate helpers.catalogloader into a thin facade, migrate imports, add deprecation warnings, commit each phase separately, run pytest -q after each phase, and produce a final summary.

---

## Steps Codex Will Execute

Phase 0 — audit catalogloader usage  
Phase 1 — migrate imports to helpers.persist  
Phase 2 — convert catalogloader to facade  
Phase 3 — add deprecation warnings  
Phase 4 — enforce persistence boundaries  

Each phase:
- separate commit
- pytest run
- summary

---

## Manual Quick Checks (Optional)

    rg -n "helpers\.catalogloader" .
    rg -n "helpers\.persist" .

Expect:
- catalogloader only in facade + tests
- persist everywhere else

---

End of file
