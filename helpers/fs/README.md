<!-- helpers/fs/README.md -->
helpers/fs
Purpose

Filesystem helpers for frontend-agnostic application code: safe path composition, directory creation, file listing, and robust file IO (including atomic writes).

Belongs here

Path safety: joining under a root, "within-root" checks

Directory creation and parent creation utilities

File listing and traversal

JSON/text/bytes read/write helpers

Atomic file writes (write-temp-then-replace)

Does not belong here

"Domain" persistence semantics (indexing, versioning, history) -> helpers/persist

Input/schema validation -> helpers/validation

In-memory tree patch paths (dict/list) -> helpers/history

Network fetch/HTTP, server concerns -> helpers/server (or similar)

Public API (flat list)
Directory / path utilities

ensure_dir(path)

ensure_parent(file_path)

ls(dir_path, pattern="*", recursive=False)

walk_files(dir_path, pattern="*", recursive=True)

find_upwards(start_dir, markers)

path_is_within(child, parent)

safe_join(root, *parts)

File operations

copy_file(src, dst)

move(src, dst)

rm(path)

rmdir(path, recursive=False, missing_ok=True)

Text / bytes IO

read_text(path, encoding="utf-8")

write_text(path, text, encoding="utf-8", ...)

read_bytes(path)

write_bytes(path, data, ...)

JSON IO

read_json(path)

read_json_default(path, default)

read_json_strict(path, root_types=(dict, list))

write_json(path, obj, indent=2, sort_keys=True, ...)

write_json_compact(path, obj, sort_keys=True, ...)

update_json(path, mutator_fn, default={}, atomic=True, ...)

Atomic writes

atomic_write_text(path, text, encoding="utf-8", overwrite=True)

atomic_write_bytes(path, data, overwrite=True)

atomic_write_json(path, obj, indent=2, sort_keys=True, overwrite=True)
