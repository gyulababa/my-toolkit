# helpers/fs/__init__.py
# Public, frontend-agnostic filesystem helpers (small primitives intended to be reused across projects).

from .dirs import (
    ensure_dir,
    ensure_parent,
    ls,
    walk_files,
    find_upwards,
    path_is_within,
    safe_join,
    rm,
    rmdir,
    copy_file,
    move,
)
from .text import (
    read_text,
    write_text,
    append_text,
    read_lines,
    write_lines,
    normalize_newlines,
)
from .bytes import (
    read_bytes,
    write_bytes,
    read_bytes_range,
    iter_file_chunks,
    hash_file,
)
from .atomic import (
    atomic_write_text,
    atomic_write_bytes,
)
from .json import (
    read_json,
    read_json_default,
    read_json_strict,
    write_json,
    write_json_compact,
    atomic_write_json,
    update_json,
)

__all__ = [
    # dirs / paths
    "ensure_dir",
    "ensure_parent",
    "ls",
    "walk_files",
    "find_upwards",
    "path_is_within",
    "safe_join",
    "rm",
    "rmdir",
    "copy_file",
    "move",
    # text
    "read_text",
    "write_text",
    "append_text",
    "read_lines",
    "write_lines",
    "normalize_newlines",
    # bytes
    "read_bytes",
    "write_bytes",
    "read_bytes_range",
    "iter_file_chunks",
    "hash_file",
    # atomic
    "atomic_write_text",
    "atomic_write_bytes",
    # json
    "read_json",
    "read_json_default",
    "read_json_strict",
    "write_json",
    "write_json_compact",
    "atomic_write_json",
    "update_json",
]
