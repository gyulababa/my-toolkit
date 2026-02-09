# helpers/fs/bytes.py
# Binary file IO helpers: read/write, partial reads, chunk iteration, and hashing.

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterator

from .dirs import ensure_parent


def read_bytes(path: str | Path) -> bytes:
    """Read raw bytes from a file."""
    return Path(path).read_bytes()


def write_bytes(path: str | Path, data: bytes | bytearray) -> None:
    """Write raw bytes to a file, creating parent directories if needed."""
    p = Path(path)
    ensure_parent(p)
    p.write_bytes(bytes(data))


def read_bytes_range(path: str | Path, start: int, length: int) -> bytes:
    """
    Read a slice of bytes from a file.

    Args:
      start: byte offset from the start of file.
      length: number of bytes to read.
    """
    if start < 0 or length < 0:
        raise ValueError("start and length must be >= 0")
    p = Path(path)
    with p.open("rb") as f:
        f.seek(start)
        return f.read(length)


def iter_file_chunks(path: str | Path, *, chunk_size: int = 1024 * 1024) -> Iterator[bytes]:
    """
    Yield file content in chunks.

    This is the preferred building block for hashing or streaming operations
    without loading the entire file into memory.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    p = Path(path)
    with p.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def hash_file(
    path: str | Path,
    *,
    algo: str = "sha256",
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Compute a hex digest for a file.

    Default is sha256 which is a good general-purpose choice for cache keys and
    integrity checks.
    """
    h = hashlib.new(algo)
    for chunk in iter_file_chunks(path, chunk_size=chunk_size):
        h.update(chunk)
    return h.hexdigest()
