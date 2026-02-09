# helpers/fs/atomic.py
# Crash-safe atomic writes (same-directory temp file + fsync + os.replace).

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from .dirs import ensure_parent


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
    - write to a temp file in the same directory
    - flush + fsync
    - os.replace() to replace the target atomically

    This reduces the risk of corrupted JSON/config files on crashes.
    """
    p = Path(path)
    if p.exists() and not overwrite:
        raise FileExistsError(str(p))
    ensure_parent(p)

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


def atomic_write_bytes(path: str | Path, data: bytes | bytearray, *, overwrite: bool = True) -> None:
    """
    Atomically write bytes to a file.

    Same semantics as atomic_write_text(), but for binary payloads (e.g. cache
    artifacts, small binary blobs).
    """
    p = Path(path)
    if p.exists() and not overwrite:
        raise FileExistsError(str(p))
    ensure_parent(p)

    fd, tmp_name = tempfile.mkstemp(prefix=p.name + ".", suffix=".tmp", dir=str(p.parent))
    tmp = Path(tmp_name)

    try:
        with os.fdopen(fd, "wb") as f:
            f.write(bytes(data))
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp), str(p))
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass
