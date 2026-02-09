# AGENTS.md — Codex / AI Coder Operating Rules (my-toolkit)

This file defines mandatory rules and workflow expectations for AI coding agents
(Codex and similar) operating on this repository.

Scope: whole repository (root).  
Priority: These rules override generic agent defaults.

---

# 0. Primary Objectives

- Prefer **mechanical, low-risk refactors** over creative rewrites.
- Keep changes **small, reviewable, and reversible**.
- Preserve **public APIs and behavior** unless explicitly instructed.
- Maintain **layered architecture boundaries** inside helpers/*.
- Ensure **tests pass after every phase** of changes.

---

# 1. Change Discipline

## 1.1 Commit discipline
- Use multiple small commits, not one large commit.
- One logical change per commit.
- Commit messages must be structured:
  - `refactor(fs): ...`
  - `refactor(persist): ...`
  - `feat(fs): ...`
  - `test: ...`
  - `chore: ...`

## 1.2 Allowed change types (default mode)

Allowed without extra instruction:
- Import rewrites
- File splits
- Function moves without behavior change
- Wrapper/facade creation
- Schema field additions (non-breaking)
- Adding validation
- Adding safety guards
- Adding new helper modules

NOT allowed unless explicitly requested:
- Renaming public classes/functions
- Removing modules used by tests
- Behavior changes
- Data format changes
- Silent schema changes
- UI behavior changes

---

# 2. Verification Requirements

After EACH phase or commit group, run:

    pytest -q

Optional additional checks:

    python -m compileall .

Never declare task complete without test run results.

---

# 3. Architecture Layering Rules

## 3.1 helpers/* is UI-free
Modules under `helpers/` must NOT import:
- dearpygui
- PySide / Qt
- tkinter
- any GUI toolkit
- preview_vision/*
- services/*

helpers/* = reusable, frontend-agnostic core utilities.

---

# 4. Filesystem Rules

## 4.1 Canonical FS modules
All filesystem operations must come from:

    helpers/fs/*

Submodules include:
- helpers/fs/atomic.py
- helpers/fs/dirs.py
- helpers/fs/text.py
- helpers/fs/json.py
- helpers/fs/bytes.py
- helpers/fs/paths.py

## 4.2 helpers/fs_utils.py status
- DO NOT delete `helpers/fs_utils.py`
- Tests depend on it
- It is treated as a **compatibility facade**
- Internal modules should migrate to helpers/fs/* instead

Rule:

> helpers/* modules must prefer helpers/fs/* over helpers.fs_utils

---

# 5. Persistence / Catalog Loader Rules

Modules:

    helpers/catalogloader/*

## 5.1 Responsibility split (required target state)
persistedloader.py = orchestration only

Must delegate to:
- persisted_paths.py → path construction only
- persisted_index.py → index schema + load/save
- helpers/fs/* → IO primitives

No mixed responsibilities.

## 5.2 Path construction rules
Do NOT scatter path literals like:
    persist_root / "index.json"
    persist_root / domain / "docs"

Instead use helpers/catalogloader/persisted_paths.py.

## 5.3 Index schema rules
Persisted index JSON must contain:
    schema_name
    schema_version

Loader must validate required fields and raise ValueError on invalid data.

## 5.4 Revision load rules
Functions:
    load_revision_raw
    load_revision_editable
    load_revision_catalog

Must:
- NOT modify index.json
- NOT change active_id
- NOT promote revisions implicitly
- Be read-only operations

---

# 6. Safe Path Handling Rules

Use safe helpers for externally influenced path parts:

    helpers/fs/paths.py

Functions:
- join_safe(root, *parts)
- ensure_under_root(root, candidate)

Rules:
- Never join user-controlled strings directly with `/`
- Always normalize + validate containment

---

# 7. Catalog / EditableCatalog Rules

Modules:
    helpers/catalog/catalog.py
    helpers/catalog/editable.py

Rules:
- Catalog objects should behave as immutable views
- EditableCatalog must deep-copy input documents
- Do not expose internal mutable references directly
- to_dict()/export methods should return safe copies

---

# 8. Mechanical Refactor Guidance (Codex Mode)

When instructions say "mechanical":

Allowed:
- search/replace imports
- move functions between files
- extract classes/dataclasses
- create wrapper modules
- update import paths

Not allowed:
- rewriting algorithms
- changing control flow
- changing return shapes
- renaming public symbols

If uncertain → keep original behavior.

---

# 9. Reporting Requirements (Final Output)

At end of task, agent must report:
- Phases completed
- Files created
- Files modified
- Imports rewritten
- Tests result summary
- Any deferred items
