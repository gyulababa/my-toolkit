# helpers/fs/dirs.py
# Path and directory utilities: create, list, traverse, copy/move/delete, and safety guards.

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional, Sequence


def ensure_dir(path: str | Path) -> Path:
    """Create a directory if it does not exist (parents=True). Returns the directory Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def ensure_parent(path: str | Path) -> Path:
    """
    Ensure the parent directory of a file path exists.

    This is a convenience wrapper used by the IO helpers so callers do not need
    to repeat: ensure_dir(Path(file_path).parent)
    """
    p = Path(path)
    return ensure_dir(p.parent)


def ls(path: str | Path, *, pattern: Optional[str] = None, recursive: bool = False) -> list[Path]:
    """
    List filesystem entries under a directory.

    Notes:
    - If the directory does not exist, returns an empty list.
    - pattern defaults to "*" (glob syntax).
    - recursive=True uses rglob() and returns descendants.
    """
    p = Path(path)
    if not p.exists():
        return []
    it = p.rglob(pattern or "*") if recursive else p.glob(pattern or "*")
    return [x for x in it]


def walk_files(root: str | Path, *, pattern: str = "*", recursive: bool = True) -> list[Path]:
    """
    List files under root (directories excluded).

    This differs from ls() by returning only files, which is a common need in
    pipelines (indexing, hashing, exporting).
    """
    entries = ls(root, pattern=pattern, recursive=recursive)
    return [p for p in entries if p.is_file()]


def find_upwards(start: str | Path, markers: Sequence[str]) -> Optional[Path]:
    """
    Walk upward from start until any marker exists (file or dir).

    Example markers:
      [".git", "pyproject.toml", "requirements.txt"]

    Returns:
      The directory containing the first found marker, or None if none found.
    """
    cur = Path(start).resolve()
    if cur.is_file():
        cur = cur.parent

    while True:
        for m in markers:
            if (cur / m).exists():
                return cur
        if cur.parent == cur:
            return None
        cur = cur.parent


def path_is_within(child: str | Path, parent: str | Path) -> bool:
    """
    Return True if child is within parent after resolution.

    Useful as a guard when users can supply paths (prevent directory traversal
    or writing outside an intended root).

    Note:
      Path.resolve() dereferences symlinks. If you need symlink-aware security
      boundaries, consider a dedicated variant and threat-model carefully.
    """
    c = Path(child).resolve()
    p = Path(parent).resolve()
    try:
        c.relative_to(p)
        return True
    except ValueError:
        return False


def safe_join(root: str | Path, *parts: str | Path) -> Path:
    """
    Join path parts to a root, and ensure the result stays within root.

    This is a convenience guard for "user-supplied relative path" scenarios.
    """
    r = Path(root)
    joined = (r.joinpath(*map(str, parts))).resolve()
    if not path_is_within(joined, r):
        raise ValueError(f"Joined path escapes root: root={r!s}, joined={joined!s}")
    return joined


def rm(path: str | Path, *, missing_ok: bool = True) -> None:
    """
    Remove a file (or symlink).

    Args:
      missing_ok: if True, a missing file is not treated as an error.
    """
    p = Path(path)
    try:
        p.unlink()
    except FileNotFoundError:
        if not missing_ok:
            raise


def rmdir(path: str | Path, *, recursive: bool = False, missing_ok: bool = True) -> None:
    """
    Remove a directory.

    Args:
      recursive: if True, remove directory tree (shutil.rmtree()).
      missing_ok: if True, a missing directory is not treated as an error.
    """
    p = Path(path)
    if not p.exists():
        if missing_ok:
            return
        raise FileNotFoundError(str(p))

    if recursive:
        shutil.rmtree(p)
    else:
        p.rmdir()


def copy_file(
    src: str | Path,
    dst: str | Path,
    *,
    overwrite: bool = True,
    preserve_metadata: bool = True,
) -> Path:
    """
    Copy a single file from src to dst.

    - Creates destination parent directories.
    - By default overwrites if dst exists (overwrite=True).
    - preserve_metadata=True uses shutil.copy2(); otherwise shutil.copy().
    """
    s = Path(src)
    d = Path(dst)
    ensure_dir(d.parent)

    if d.exists() and not overwrite:
        raise FileExistsError(str(d))

    copier = shutil.copy2 if preserve_metadata else shutil.copy
    copier(str(s), str(d))
    return d


def move(src: str | Path, dst: str | Path, *, overwrite: bool = True) -> Path:
    """
    Move/rename src to dst.

    - Creates destination parent directories.
    - overwrite=False raises if dst exists.
    """
    s = Path(src)
    d = Path(dst)
    ensure_dir(d.parent)

    if d.exists() and not overwrite:
        raise FileExistsError(str(d))

    # shutil.move handles cross-filesystem moves.
    shutil.move(str(s), str(d))
    return d
