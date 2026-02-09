# AGENTS.md — Codex / AI Coder Operating Rules (my-toolkit)

Scope: whole repository.  
These rules override generic agent defaults.

Primary mode: SAFE REFACTOR + ARCHITECTURE ENFORCEMENT + TEST GUARDRAILS

# Task Registry Authority (Hard Rule)

- Codex executes ONLY tasks listed in CODEX_TASKS.md.
- CODEX_FUTURE_PLANS.md is non-executable roadmap text.
- Each completed task must be marked DONE in CODEX_TASKS.md and must include:
  COMMIT=<sha> and DATE=<YYYY-MM-DD>.
- If blocked, set STATUS=SKIP and record a short rationale in the final summary.

# Task Registry Format Protection

Codex must NOT rewrite task registry lines except:
- checkbox
- STATUS field
- COMMIT field
- DATE field

Do not reflow, rewrap, or rephrase registry task lines.

---

# 0. Current Architecture Baseline (FACT)

Already implemented:

- helpers.persist/* = canonical persistence API
- helpers.catalogloader/* = deprecated forwarding facade
- Internal imports already migrated
- Tests are green

Agents must treat this as baseline truth — do NOT try to redo migration.

---

# 1. Core Objectives

- Keep changes small and reviewable
- Prefer mechanical refactors over rewrites
- Preserve behavior and public APIs unless explicitly told otherwise
- Enforce architecture boundaries
- Add guardrail tests instead of big rewrites
- Keep tests passing after each phase

---

# 2. Commit Rules

One logical change per commit.

Prefixes:

- refactor(imports):
- refactor(persist):
- refactor(fs):
- test(architecture):
- feat(guardrail):
- fix(tests):
- chore(docs):

Never mix behavior change with refactor in the same commit.

---

# 2.a Commit SHA Registry Rule

Allowed:
- exactly one `git commit --amend --no-edit` per task, solely to inject COMMIT=<sha> into registry/history task lines

Not allowed:
- any other amendments
- altering files unrelated to registry/history task lines during the amend

---

# 3. Verification Rules

After every phase:

    pytest -q

Optional:

    python -m compileall .

Do not declare completion without test results.

---

# 4. Persistence Authority Map

## Canonical

    helpers.persist.*

Owns:
- persistence layout
- index schema
- revisions
- loaders/savers

## Deprecated Facade (helpers.catalogloader.*)

Allowed changes ONLY:
- forwarding imports / re-exports to helpers.persist.*
- thin wrappers that call helpers.persist
- DeprecationWarning emission
- docstrings/comments clarifying deprecation
- test compatibility fixes (import paths), no behavior changes

Forbidden in helpers.catalogloader/*:
- implementing persistence logic
- filesystem writes (other than calling helpers.persist)
- path layout logic
- schema validation logic
- new public API surface

Clarification:
- Forbidden in helpers/* (except helpers/catalogloader/*): importing helpers.catalogloader
- Allowed but discouraged in services/*: importing helpers.catalogloader (migrate when touched)


---

# 5.a helpers/* Layering Rules

helpers/* must remain frontend-agnostic.

Must NOT import:
- dearpygui
- Qt / PySide
- tkinter
- preview_vision/*
- services/*
- UI frameworks

# 5.b Forbidden Imports in helpers/* (Hard Rule)

Files under helpers/* must NOT import modules matching these substrings:

- dearpygui
- PySide
- Qt
- tkinter
- preview_vision
- services
- requests
- subprocess

Exception: helpers/toolkits/* may import network or subprocess libraries if required.


---


# 6. Filesystem Rules

Canonical FS helpers:

    helpers/fs/*

helpers/fs_utils.py:
- compatibility facade
- keep for tests
- do not delete
- prefer helpers/fs/* in new code

# Dependency Policy

- Do NOT add new third-party dependencies without explicit instruction.
- Prefer stdlib or existing helpers modules.


---

# 7. Safe Path Rules

Use:

    helpers/fs/paths.py

Functions:
- join_safe
- ensure_under_root

Never join user-controlled strings directly with `/`.

---

# 8. Mechanical Refactor Mode

Allowed:
- import rewrites
- wrapper/facade creation
- test additions
- guardrail tests
- type hints
- doc updates

Not allowed:
- algorithm rewrites
- return-shape changes
- public symbol renames

If uncertain → preserve behavior.

---

# 9. Diff Hygiene (Hard Rule)

- Do not run global formatters unless explicitly instructed.
- Do not reorder imports or rewrap lines unless required for the change.
- Avoid whitespace-only edits.
- Limit changes to the minimum necessary lines.

---


# 10. Multi-file Refactor Protocol

Before any multi-file import rewrite or mechanical replacement:
1) run ripgrep to list all matches
2) apply changes only to intended files (exclude tests unless instructed)
3) run pytest -q
4) commit

---

# 11. Required Guardrails (Going Forward)

Agents should prefer adding:

- architecture import tests
- helpers/catalogloader import guard (helpers/* must not import helpers.catalogloader outside helpers/catalogloader/*)
- persist boundary guards (persistence markers confined to helpers/persist/* and helpers/catalogloader/*)
- helpers/* forbidden import guard (UI frameworks, services, requests, subprocess)
- boundary enforcement tests
- facade consistency tests
- deprecation warning tests

over large structural edits.

---

# 12. Definition of Done (Must Satisfy)

- pytest -q passes
- CODEX_TASKS.md updated (DONE/SKIP + COMMIT + DATE)
- If workflow or task model changed: update RUN_CODEX_REFACTOR.md and AGENTS.md
- Final summary includes:
  - completed task IDs
  - commit SHAs
  - pytest output status
  - any skipped tasks with rationale

---


# 13. Reporting Requirements

Final report must include:

- files changed
- tests added
- guardrails added
- violations fixed (if any)
- pytest results
- docs updated (if workflow changed)
