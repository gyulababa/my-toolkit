# helpers/fs_utils.py
from __future__ import annotations

"""
helpers.fs_utils
----------------

Small filesystem helpers for consistent IO patterns.

Design goals:
- Keep functions composable and predictable.
- Ensure write helpers create parent directories.
- Provide atomic write variants for config/state files to reduce corruption risk.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional, Sequence


# ─────────────────────────────────────────────────────────────
# Directories / listing
# ─────────────────────────────────────────────────────────────

def ensure_dir(path: str | Path) -> Path:
    """Create directory if missing (parents=True). Returns Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def ls(path: str | Path, *, pattern: Optional[str] = None, recursive: bool = False) -> list[Path]:
    """
    List files/dirs under path.

    - pattern defaults to "*" (glob)
    - recursive uses rglob()
    """
    p = Path(path)
    if not p.exists():
        return []
    it = p.rglob(pattern or "*") if recursive else p.glob(pattern or "*")
    return [x for x in it]


def find_upwards(start: str | Path, markers: Sequence[str]) -> Optional[Path]:
    """
    Walk upward from start until any marker exists (file or dir).

    Example markers:
      [".git", "pyproject.toml", "requirements.txt"]
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
    Return True if child is within parent (after resolving).

    Useful as a guard when users can supply paths (prevent directory traversal
    or writing outside an intended root).
    """
    c = Path(child).resolve()
    p = Path(parent).resolve()
    try:
        c.relative_to(p)
        return True
    except ValueError:
        return False


# ─────────────────────────────────────────────────────────────
# Text IO
# ─────────────────────────────────────────────────────────────

def read_text(path: str | Path, *, encoding: str = "utf-8") -> str:
    """Read text from a file."""
    return Path(path).read_text(encoding=encoding)


def write_text(path: str | Path, text: str, *, encoding: str = "utf-8") -> None:
    """Write text to a file, creating parent directories if needed."""
    p = Path(path)
    ensure_dir(p.parent)
    p.write_text(text, encoding=encoding)


def atomic_write_text(
    path: str | Path,
    text: str,
    *,
    encoding: str = "utf-8",
    overwrite: bool = True,
) -> None:
    """
    Atomically write text to a file.

    Implementation:
    - writes to a temp file in the same directory
    - flush + fsync
    - os.replace() to replace target atomically

    This reduces the risk of corrupted JSON/config files on crashes.
    """
    p = Path(path)
    if p.exists() and not overwrite:
        raise FileExistsError(str(p))
    ensure_dir(p.parent)

    fd, tmp_name = tempfile.mkstemp(prefix=p.name + ".", suffix=".tmp", dir=str(p.parent))
    tmp = Path(tmp_name)

    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp), str(p))
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────
# Bytes IO
# ─────────────────────────────────────────────────────────────

def read_bytes(path: str | Path) -> bytes:
    """Read raw bytes from a file."""
    return Path(path).read_bytes()


def write_bytes(path: str | Path, data: bytes | bytearray) -> None:
    """Write raw bytes to a file, creating parent directories if needed."""
    p = Path(path)
    ensure_dir(p.parent)
    p.write_bytes(bytes(data))


# ─────────────────────────────────────────────────────────────
# JSON IO
# ─────────────────────────────────────────────────────────────

def read_json(path: str | Path, *, encoding: str = "utf-8") -> Any:
    """Read JSON from a file and return the decoded object."""
    return json.loads(read_text(path, encoding=encoding))


def write_json(
    path: str | Path,
    data: Any,
    *,
    encoding: str = "utf-8",
    indent: int = 2,
    sort_keys: bool = True,
) -> None:
    """Write JSON to a file (non-atomic), creating parent directories if needed."""
    p = Path(path)
    ensure_dir(p.parent)
    p.write_text(
        json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False),
        encoding=encoding,
    )


def atomic_write_json(
    path: str | Path,
    data: Any,
    *,
    encoding: str = "utf-8",
    indent: int = 2,
    sort_keys: bool = True,
    overwrite: bool = True,
) -> None:
    """
    Atomically write JSON to a file.

    Uses atomic_write_text() under the hood. Recommended for:
    - user-edited config files
    - app state files
    - caches that should not end up half-written
    """
    payload = json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
    atomic_write_text(path, payload, encoding=encoding, overwrite=overwrite)
