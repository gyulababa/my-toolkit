# CODEX_TASKS.md — Push-button refactor (my-toolkit root)

## Goal summary
1) Internal code must stop importing helpers.fs_utils (keep it for tests/backcompat).
2) Split helpers/catalogloader/persistedloader.py into:
   - helpers/catalogloader/persisted_paths.py (path building only)
   - helpers/catalogloader/persisted_index.py (index schema + load/save)
   - persistedloader.py becomes orchestrator
3) Add helpers/fs/paths.py for join_safe + ensure_under_root and use it where user-controlled parts are joined.
4) Ensure load_revision_* APIs exist and do NOT promote active.

## Global rules
- Do NOT delete helpers/fs_utils.py (tests import it).
- Keep public APIs stable unless explicitly stated.
- Mechanical refactor only; no behavior changes unless tests force it.
- Run `pytest -q` after each phase.

---

# Phase 0 — Baseline
1) Run: `pytest -q` and record output.
2) Inventory of internal fs_utils usage:
   - `rg -n "from helpers\.fs_utils import|import helpers\.fs_utils|helpers\.fs_utils\." helpers preview_vision services`
3) Inventory persisted path literals:
   - `rg -n "persist_root\s*/\s*\"|/ \"index\.json\"|/ \"docs\"|revisions|active_id|next_int" helpers`

---

# Phase 1 — Stop importing helpers.fs_utils internally (keep facade)
## 1A) persistedloader import change (known)
Edit: helpers/catalogloader/persistedloader.py
- Replace:
  `from helpers.fs_utils import ensure_dir, atomic_write_text  # later: helpers.fs.*`
- With:
  `from helpers.fs.dirs import ensure_dir`
  `from helpers.fs.text import atomic_write_text`

## 1B) Any other internal imports found in Phase 0
For each file in helpers/ preview_vision/ services/ that imports helpers.fs_utils:
- Replace imports with helpers/fs/* equivalents where available:
  - ensure_dir -> helpers.fs.dirs.ensure_dir
  - atomic_write_text -> helpers.fs.text.atomic_write_text
  - read_text/write_text -> helpers.fs.text.read_text/write_text
  - read_json/write_json -> helpers.fs.json.read_json/write_json
  - atomic_write_json -> helpers.fs.json.atomic_write_json
  - read_bytes/write_bytes -> helpers.fs.bytes.read_bytes/write_bytes
If a function only exists in helpers/fs_utils.py (ls, find_upwards, path_is_within), keep using fs_utils ONLY in callers outside helpers/* (prefer migrating later) OR move that function into helpers/fs/paths.py and have fs_utils re-export it.

## 1C) Keep helpers/fs_utils.py as facade (optional tighten)
- If helpers/fs_utils.py duplicates implementations that exist in helpers/fs/*, refactor it to call helpers/fs/* to avoid divergence.
- Ensure tests/test_fs_utils.py still passes.

Verify: `pytest -q`

Commit: `refactor(fs): stop importing helpers.fs_utils internally`

---

# Phase 2 — Split persistedloader
Create:
- helpers/catalogloader/persisted_paths.py
- helpers/catalogloader/persisted_index.py

## 2A) persisted_paths.py (paths only)
Implement pure path helpers currently embedded in persistedloader.py:
- index_path(persist_root: Path, domain: str) -> Path
- domain_root(persist_root: Path, domain: str) -> Path
- docs_root(persist_root: Path, domain: str) -> Path
- doc_dir(persist_root: Path, domain: str, doc_id: str) -> Path
- revisions_dir(persist_root: Path, domain: str, doc_id: str) -> Path
- revision_path(...) if applicable

Rule: NO json IO here. Only Path joining.

## 2B) persisted_index.py (index schema + IO)
Move from helpers/catalogloader/persistedloader.py:
- PersistIndex dataclass
- any index JSON load/save helpers
- any next_id generation logic

Add/ensure:
- schema_name + schema_version enforced on write
- validation: raise ValueError on missing/invalid fields

Provide:
- load_index(persist_root: Path, domain: str) -> PersistIndex
- save_index(persist_root: Path, domain: str, index: PersistIndex) -> None

## 2C) persistedloader.py becomes orchestrator
Update helpers/catalogloader/persistedloader.py:
- Replace inline path literals (`persist_root / domain / "index.json"` etc.) with persisted_paths.*
- Replace inline index read/write logic with persisted_index.load_index/save_index
- Keep existing public methods and behavior unchanged.

## 2D) exports
Update helpers/catalogloader/__init__.py:
- Export PersistedCatalogLoader as before
- Optionally export PersistIndex/load_index/save_index if used externally

Verify: `pytest -q`

Commit: `refactor(persist): extract persisted_paths and persisted_index`

---

# Phase 3 — Safe path helpers
Create: helpers/fs/paths.py with:
- join_safe(root: Path, *parts: str) -> Path
- ensure_under_root(root: Path, candidate: Path) -> Path

Integrate:
- Use join_safe in helpers/catalogloader/persisted_paths.py where doc_id/domain may be externally influenced.
- Keep behavior identical for normal inputs; only add safety checks.

Verify: `pytest -q`

Commit: `feat(fs): add safe path helpers`

---

# Phase 4 — Non-promoting revision load APIs
In helpers/catalogloader/persistedloader.py:
Ensure these functions exist (or add them) and they MUST NOT promote the revision to active:
- load_revision_raw(persist_root, domain, doc_id)
- load_revision_editable(persist_root, domain, doc_id, history=None)
- load_revision_catalog(persist_root, domain, doc_id)

Rules:
- must read the specified revision/doc without modifying index.json
- must not change active_id
- must not write anything unless explicitly requested by caller

Verify: `pytest -q`

Commit: `feat(persist): add non-promoting load_revision_* APIs`

---

# Deliverable summary
- Separate commits per phase
- Final report: files changed + test outputs
