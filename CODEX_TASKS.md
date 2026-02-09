# CODEX_TASKS.md — Push-button refactor (my-toolkit root, idempotent)

## Goal summary (target state)
1) Internal code must NOT import helpers.fs_utils (keep fs_utils for tests/backcompat).
2) Persisted loader boundaries:
   - helpers/catalogloader/persisted_paths.py = path building only (no IO)
   - helpers/catalogloader/persisted_index.py = index schema + load/save + validation
   - helpers/catalogloader/persistedloader.py = orchestration only
3) Safe path utilities exist and are used where user-controlled strings are joined:
   - helpers/fs/paths.py with join_safe + ensure_under_root
4) load_revision_* APIs exist and are read-only (no promotion / no index writes).

## Global rules
- Do NOT delete helpers/fs_utils.py (tests import it).
- Mechanical refactor only; no behavior changes unless tests force it.
- Run `pytest -q` after each phase.

---

# Phase 0 — Baseline / audit
1) Run: `pytest -q` and record output.
2) Confirm internal fs_utils usage is eliminated:
   - `rg -n "helpers\.fs_utils" helpers preview_vision services`
   Expect: no hits.
3) Confirm fs_utils remains for tests:
   - `rg -n "helpers\.fs_utils" tests helpers/fs_utils.py`
   Expect: tests + facade only.
4) Confirm persisted modules exist:
   - helpers/catalogloader/persisted_paths.py
   - helpers/catalogloader/persisted_index.py
   - helpers/fs/paths.py

Commit (optional): `chore(audit): record baseline status`

---

# Phase 1 — Fix doc/spec drift + correct FS mappings (mechanical)
Update any instructions or imports that wrongly suggest atomic_write_text is in helpers.fs.text.
Canonical mapping in THIS repo:
- atomic_write_text -> helpers.fs.atomic.atomic_write_text
- ensure_dir -> helpers.fs.dirs.ensure_dir
- read_text/write_text -> helpers.fs.text.read_text/write_text
- read_json/write_json/atomic_write_json -> helpers.fs.json.*
- read_bytes/write_bytes -> helpers.fs.bytes.*

Actions:
1) Search for incorrect mapping references:
   - `rg -n "fs\.text import atomic_write_text|helpers\.fs\.text\.atomic_write_text" .`
2) Replace them with the correct mapping to helpers.fs.atomic where applicable.

Verify: `pytest -q`

Commit: `chore(docs): align CODEX specs to current implementation`

---

# Phase 2 — Persisted loader boundary enforcement (audit + tighten)
Goal: ensure responsibilities are clean, not duplicated.

1) persisted_paths.py:
   - Must contain ONLY path construction helpers
   - Must NOT read/write JSON
   - Must NOT import helpers.fs.json or helpers.fs.atomic
   - It MAY import helpers.fs.paths (join_safe) and pathlib.

2) persisted_index.py:
   - Owns PersistIndex schema, validation, load/save index
   - Ensures schema_name + schema_version on write
   - Raises ValueError on invalid index

3) persistedloader.py:
   - Orchestrates using persisted_paths + persisted_index + catalog loader logic
   - No scattered `persist_root / "index.json"` literals outside persisted_paths

Actions:
- `rg -n "persist_root\s*/\s*\"|/ \"index\.json\"|/ \"docs\"" helpers/catalogloader`
- Replace any remaining literals with persisted_paths helpers.
- Ensure persistedloader imports index functions from persisted_index.

Verify: `pytest -q`

Commit: `refactor(persist): enforce persisted_* module boundaries`

---

# Phase 3 — Safe path usage in persistence layer (tighten)
Goal: wherever doc_id/domain might come from outside, use join_safe / ensure_under_root.

Actions:
1) Ensure persisted_paths.py uses helpers.fs.paths.join_safe for externally influenced parts.
2) Ensure any functions that accept user-supplied IDs validate containment.

Verify: `pytest -q`

Commit: `refactor(fs): use safe path helpers in persisted paths`

---

# Phase 4 — Revision load APIs read-only guarantee
Ensure in helpers/catalogloader/persistedloader.py:
- load_revision_raw(...)
- load_revision_editable(..., history=None)
- load_revision_catalog(...)

Rules:
- Must NOT write index.json
- Must NOT change active_id
- Must NOT promote revisions

Actions:
- `rg -n "def load_revision_" helpers/catalogloader/persistedloader.py`
- Inspect for any writes and remove them from these functions (keep read-only).
- Add minimal tests if missing (only if needed to prevent regression).

Verify: `pytest -q`

Commit: `feat(persist): guarantee read-only load_revision_* APIs`

---

# Deliverable summary
At end, report:
- phases completed
- files changed/created
- imports rewritten
- test output summary
- any deferred items
