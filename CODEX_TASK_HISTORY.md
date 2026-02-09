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
4) Use a registry-update commit to record COMMIT=<task_sha> and DATE from the task commit; never amend the task commit for registry updates

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
- [x] ID=T0103 STATUS=DONE TYPE=doc SCOPE=CODEX_* VERIFY="pytest -q" DESC="Doc maintenance: remove completed items from CODEX_FUTURE_PLANS.md; create CODEX_TASK_HISTORY.md using the same registry line format; move all STATUS=DONE tasks from CODEX_TASKS.md into CODEX_TASK_HISTORY.md without rewriting their fields" COMMIT=9dade7d DATE=2026-02-09
- [x] ID=T0104 STATUS=DONE TYPE=doc SCOPE=AGENTS.md VERIFY="pytest -q" DESC="Update AGENTS.md: add Commit SHA Registry Rule section allowing exactly one git commit --amend --no-edit solely to inject COMMIT=<sha> into registry/history task lines" COMMIT=a3bc25a DATE=2026-02-09
- [x] ID=T0105 STATUS=DONE TYPE=doc SCOPE=AGENTS.md,CODEX_TASKS.md,RUN_CODEX_REFACTOR.md VERIFY="pytest -q" DESC="Adjust registry rules to allow one extra amend OR a post-commit registry update so COMMIT=<sha> matches final amended hash (fix mismatch like T0104 pre-amend vs final hash)" COMMIT=bb77427 DATE=2026-02-09
- [x] ID=T0106 STATUS=DONE TYPE=doc SCOPE=CODEX_TASKS.md,CODEX_TASK_HISTORY.md,RUN_CODEX_REFACTOR.md VERIFY="pytest -q" DESC="Enforce DONE-task archival: define mandatory rule that after any run, all STATUS=DONE tasks are copied verbatim into CODEX_TASK_HISTORY.md and removed from CODEX_TASKS.md (append-only history), and update RUN to require it" COMMIT=13eff11 DATE=2026-02-09
- [x] ID=T0107 STATUS=DONE TYPE=doc SCOPE=AGENTS.md,RUN_CODEX_REFACTOR.md,CODEX_TASKS.md,CODEX_TASK_HISTORY.md VERIFY="pytest -q" DESC="Fix self-referential COMMIT hash rule: stop using amend for registry updates; require separate post-task commit to record COMMIT=<task_sha> in history (no recursion), and update docs to define task commit vs registry-update commit" COMMIT=42471ef DATE=2026-02-09
- [x] ID=T0108 STATUS=DONE TYPE=fix SCOPE=services/vision/preview_session.py VERIFY="pytest -q" DESC="Remove services->preview_vision import by injecting config/source builder callables into VisionPreviewSession" COMMIT=6e73069 DATE=2026-02-09
- [x] ID=T0109 STATUS=DONE TYPE=refactor SCOPE=services/vision VERIFY="pytest -q" DESC="Introduce services.vision interfaces/types for FrameSource factory and config loader to keep preview app as wiring only" COMMIT=f734197 DATE=2026-02-09
- [x] ID=T0110 STATUS=DONE TYPE=refactor SCOPE=services/vision/dpg_* VERIFY="pytest -q" DESC="Move DearPyGui-specific modules out of services/vision into app/adapters/dearpygui/vision" COMMIT=4bbd763 DATE=2026-02-09
