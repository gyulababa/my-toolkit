# RUN_CODEX_REFACTOR.md

## Control Chain

Execution order and authority:

1. RUN_CODEX_REFACTOR.md (this file) — execution driver
2. AGENTS.md — mandatory behavioral + architecture rules
3. CODEX_TASKS.md — mechanical refactor steps

If instructions conflict:
AGENTS.md > RUN_CODEX_REFACTOR.md > CODEX_TASKS.md

This file contains the exact one-line prompt + procedure to run the Codex refactor plan
for this repository (my-toolkit/).

Prerequisites:
- You have installed and configured Codex in your editor (VS Code, Codex CLI, or similar).
- `AGENTS.md` and `CODEX_TASKS.md` exist at project root.
- Tests are runnable via `pytest -q`.

---

## One-Line Start Prompt (Codex)

Follow RUN_CODEX_REFACTOR.md exactly. Execute all phases defined here and in CODEX_TASKS.md, obey AGENTS.md rules, commit each phase separately, run pytest -q after each phase, and output the required completion summary.



---

## How to Run

1. Open the repository in VS Code.
2. Open the Codex extension (or start the Codex CLI).
3. Paste the one-line prompt above into the Codex input window.
4. Hit **Run/Execute**.
5. Review each generated commit in the Codex editor, one at a time.
6. After each phase Codex completes, verify tests pass:  
   ```bash
   pytest -q
7. At completion, Codex should output a summary according to AGENTS.md rules.

Expected Codex Workflow

After the one line prompt, Codex should:

Phase 0 — Baseline

Run tests

Report current test status

Phase 1 — Stop internal helpers.fs_utils imports

Apply mechanical search/replace on imports

Update persistence loader

Run tests

Phase 2 — Extract persisted paths + index

Create persisted_paths.py, persisted_index.py

Refactor persistedloader.py

Update exports

Run tests

Phase 3 — Safe path helpers

Create helpers/fs/paths.py

Integrate into persisted_paths.py

Run tests

Phase 4 — Add non-promoting load_revision_ APIs*

Add APIs to persistedloader

Run tests

Final Summary
Codex should output:

Files changed/created

Tests results

Any unresolved items

Manual Verification Checklist (for you)

When Codex completes, verify:

No internal module imports helpers.fs_utils anymore (except tests).

All persistence path logic lives in persisted_paths.py.

Index read/write logic in persisted_index.py.

Safe path helpers used where user input influences paths.

No public API changes without test updates.

All tests pass.

If something breaks

If pytest fails or Codex produces unwanted behavior:

Stop and revert that commit.

Fix the test or ask Codex to fix broken behavior with clear instructions.

Do not combine refactor and bug fix in the same commit.

Exit Criteria

After Codex finishes:

All phases completed

All tests passing

Summary written as per AGENTS.md

Then you can merge or continue manual work.

End of RUN_CODEX_REFACTOR.md