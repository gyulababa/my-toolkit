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

These are strict.

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

## 3.2 Filesystem access rules

### Canonical FS modules
All filesystem operations must come from:

helpers/fs/*


Submodules include:
- helpers/fs/atomic.py
- helpers/fs/dirs.py
- helpers/fs/text.py
- helpers/fs/json.py
- helpers/fs/bytes.py
- helpers/fs/paths.py (new safe path layer)

### helpers/fs_utils.py status
- DO NOT delete `helpers/fs_utils.py`
- Tests depend on it
- It is treated as a **compatibility facade**
- Internal modules should migrate to helpers/fs/* instead

Rule:

> helpers/* modules must prefer helpers/fs/* over helpers/fs_utils.py

---

# 4. Persistence / Catalog Loader Rules

Modules:

helpers/catalogloader/*


## 4.1 Responsibility split (required target state)

persistedloader.py = orchestration only

Must delegate to:

- persisted_paths.py → path construction only
- persisted_index.py → index schema + load/save
- helpers/fs/* → IO primitives

No mixed responsibilities.

---

## 4.2 Path construction rules

Do NOT scatter path literals like:


persist_root / "index.json"
persist_root / domain / "docs"


Instead use:

helpers/catalogloader/persisted_paths.py


All persisted layout knowledge must live there.

---

## 4.3 Index schema rules

Persisted index JSON must contain:

schema_name
schema_version


Loader must validate required fields and raise ValueError on invalid data.

---

## 4.4 Revision load rules

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

# 5. Safe Path Handling Rules

Use safe helpers for externally influenced path parts.

Module:

helpers/fs/paths.py


Functions:

- join_safe(root, *parts)
- ensure_under_root(root, candidate)

Rules:

- Never join user-controlled strings directly with `/`
- Always normalize + validate containment

---

# 6. Catalog / EditableCatalog Rules

Modules:

helpers/catalog/catalog.py
helpers/catalog/editable.py


Rules:

- Catalog objects should behave as immutable views
- EditableCatalog must deep-copy input documents
- Do not expose internal mutable references directly
- to_dict()/export methods should return safe copies

---

# 7. Tags Subsystem Rules

Modules:

helpers/tags/*


Rules:

- Query logic separated from data containers
- TagQuery objects are serializable
- Index structures (if added) must be optional acceleration layers
- No IO inside pure tag model classes

---

# 8. Config Defaults Rules

If working with helpers/configs:

- Default configs must validate on load
- Validation must be explicit
- Silent fallback is not allowed
- Missing required fields must raise

---

# 9. Mechanical Refactor Guidance (Codex Mode)

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

# 10. Search / Replace Safety

Before global replacement:

1. Run ripgrep search
2. List matched files
3. Exclude:
   - tests (unless instructed)
   - compatibility facades
4. Apply change
5. Run tests

Never blind-replace across repo without match review.

---

# 11. Test Protection Rules

- Tests are authoritative for behavior
- Do not rewrite tests to make failures disappear
- Only update tests if:
  - import paths changed
  - module split requires path update
- If behavior conflict appears → stop and report

---

# 12. Reporting Requirements (Final Output)

At end of task, agent must report:

- Phases completed
- Files created
- Files modified
- Imports rewritten
- Tests result summary
- Any deferred items

---

# 13. Default Execution Mode

Unless instructed otherwise:

> Operate in SAFE REFACTOR MODE

Meaning:
- No behavior change
- No public API change
- No schema change
- Only structural improvements

---

End of AGENTS.md
