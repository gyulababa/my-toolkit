# RUN_CODEX_REFACTOR.md

## Control Chain

Execution order and authority:

1. RUN_CODEX_REFACTOR.md (this file) — execution driver
2. AGENTS.md — mandatory behavioral + architecture rules
3. CODEX_TASKS.md — mechanical refactor steps

If instructions conflict:
AGENTS.md > RUN_CODEX_REFACTOR.md > CODEX_TASKS.md

---

This file contains the exact one-line prompt + procedure to run the Codex refactor plan.
This workflow is **idempotent**: it audits current state first and only applies missing changes.

Prerequisites:
- `AGENTS.md` and `CODEX_TASKS.md` exist at project root
- Tests runnable via `pytest -q`

---

## One-Line Start Prompt (Codex in VS Code)

Copy/paste into Codex:

Follow RUN_CODEX_REFACTOR.md exactly. Obey AGENTS.md rules. Execute the audit + phases in CODEX_TASKS.md, commit each phase separately, run `pytest -q` after each phase, and finish with a summary: phases completed, files created/modified, imports rewritten, and test results.

---

## How to Run

1) Open repo in VS Code
2) Open Codex panel
3) Paste the one-line prompt above
4) Review each phase commit
5) Ensure pytest passes after each phase

---

## Manual quick checks (optional)

From repo root:

- Internal fs_utils usage should be gone:
  rg -n "helpers\.fs_utils" helpers preview_vision services

- Persisted path literals should be centralized:
  rg -n "persist_root\s*/\s*\"|/ \"index\.json\"|/ \"docs\"" helpers/catalogloader

- load_revision_* must be read-only:
  rg -n "def load_revision_" helpers/catalogloader/persistedloader.py

---

End of RUN_CODEX_REFACTOR.md
