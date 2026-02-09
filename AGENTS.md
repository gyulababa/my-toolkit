# AGENTS.md — Codex / AI Coder Operating Rules (my-toolkit)

Scope: whole repository.  
These rules override generic agent defaults.

Primary mode: SAFE REFACTOR + ARCHITECTURE ENFORCEMENT

---

# 0. Core Objectives

- Keep changes small and reviewable
- Prefer mechanical refactors over rewrites
- Preserve behavior and public APIs unless explicitly told otherwise
- Enforce architecture boundaries
- Keep tests passing after each phase

---

# 1. Commit Rules

One logical change per commit.

Use structured prefixes:

- refactor(persist):
- refactor(fs):
- refactor(imports):
- feat(persist):
- fix(tests):
- chore(docs):

Never mix refactor + behavior change in one commit.

---

# 2. Verification Rules

After every phase:

    pytest -q

Optional:

    python -m compileall .

Do not declare completion without test results.

---

# 3. Architecture Authority Map (CURRENT TRUTH)

## Persistence Layer — CANONICAL

helpers/persist/* is the canonical persistence API.

All new code must use:

    helpers.persist.*

This layer owns:
- persisted document storage
- revisions
- index handling
- persistence schemas
- loaders/savers

## Catalog Loader — DEPRECATED COMPAT LAYER

helpers/catalogloader/* is deprecated compatibility.

Rules:

- Do not add new features here
- Do not expand APIs
- Only allowed changes:
  - thin wrappers
  - forwarding adapters
  - deprecation warnings
  - import redirects

New code must NOT depend on helpers.catalogloader.

---

# 4. helpers/* Layering Rules

helpers/* must remain frontend-agnostic.

Must NOT import:
- dearpygui
- PySide / Qt
- tkinter
- preview_vision/*
- services/*
- any UI framework

---

# 5. Filesystem Rules

Canonical FS helpers live in:

    helpers/fs/*

Modules:
- atomic
- dirs
- text
- json
- bytes
- paths

## helpers/fs_utils.py

- Keep for compatibility + tests
- Do not delete
- Treat as facade
- helpers/* modules should prefer helpers/fs/* directly

---

# 6. Safe Path Rules

Use helpers/fs/paths.py:

- join_safe
- ensure_under_root

Never join user-controlled strings directly with `/`.

---

# 7. Catalog / EditableCatalog Rules

helpers/catalog/*:

- Catalog behaves immutable
- EditableCatalog deep-copies inputs
- No mutable references leaked
- Export returns safe copies

---

# 8. Persistence Rules

helpers/persist/* is source of truth.

Rules:

- Path layout logic centralized
- Index schema must include:
  - schema_name
  - schema_version
- Load-revision APIs must be read-only
- No scattered persistence path literals outside persist helpers

---

# 9. Mechanical Refactor Mode (Default)

Allowed:
- import rewrites
- module moves
- facade wrappers
- deprecation redirects
- path centralization

Not allowed:
- algorithm rewrites
- return-shape changes
- public symbol renames

If uncertain → preserve behavior.

---

# 10. Test Authority

Tests define behavior.

- Do not rewrite tests to hide failures
- Only update imports if module paths change
- Missing legacy symbols may be restored via compatibility shims

---

# 11. Reporting Requirements

Final report must include:

- phases completed
- files changed
- imports rewritten
- deprecated usages found
- test results
