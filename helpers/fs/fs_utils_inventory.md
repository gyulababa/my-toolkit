# helpers/fs_utils parity inventory

Source file: helpers/fs_utils.py (snapshot date: 2026-02-10)

Function | helpers/fs module | Notes
ensure_dir | helpers/fs/dirs.py | Same behavior.
ls | helpers/fs/dirs.py | Same behavior.
find_upwards | helpers/fs/dirs.py | Same behavior.
path_is_within | helpers/fs/dirs.py | Same behavior (helpers/fs version adds note about symlinks).
read_text | helpers/fs/text.py | Same behavior.
write_text | helpers/fs/text.py | Same behavior; helpers/fs uses ensure_parent.
atomic_write_text | helpers/fs/atomic.py | Same behavior.
read_bytes | helpers/fs/bytes.py | Same behavior.
write_bytes | helpers/fs/bytes.py | Same behavior; helpers/fs uses ensure_parent.
read_json | helpers/fs/json.py | Same behavior; helpers/fs adds explicit empty-file JSONDecodeError messaging.
write_json | helpers/fs/json.py | Same behavior.
atomic_write_json | helpers/fs/json.py | Same behavior.

Gaps: none detected (helpers/fs covers all helpers/fs_utils functions).
Overlaps: all helpers/fs_utils functions overlap with helpers/fs equivalents.
T0204 result: no missing helpers/fs_utils functions to move; no import updates required.
