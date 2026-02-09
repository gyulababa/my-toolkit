# helpers/fs/text.py
# Text file IO helpers: read/write/append and line-oriented utilities.

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .dirs import ensure_parent


def read_text(path: str | Path, *, encoding: str = "utf-8") -> str:
    """Read text from a file."""
    return Path(path).read_text(encoding=encoding)


def write_text(path: str | Path, text: str, *, encoding: str = "utf-8") -> None:
    """
    Write text to a file, creating parent directories if needed.

    This is non-atomic. If you need crash-safe writes for user-edited config/state,
    prefer atomic_write_text() from helpers.fs.atomic.
    """
    p = Path(path)
    ensure_parent(p)
    p.write_text(text, encoding=encoding)


def append_text(path: str | Path, text: str, *, encoding: str = "utf-8") -> None:
    """
    Append text to a file, creating parent directories if needed.

    Note: append is not atomic with respect to interleaving writes from multiple
    processes. Use a lock if you need strong guarantees.
    """
    p = Path(path)
    ensure_parent(p)
    with p.open("a", encoding=encoding) as f:
        f.write(text)


def read_lines(
    path: str | Path,
    *,
    encoding: str = "utf-8",
    strip_newline: bool = True,
) -> list[str]:
    """
    Read a text file as a list of lines.

    Args:
      strip_newline: if True, strips trailing "\n"/"\r\n" from each line.
    """
    keepends = not strip_newline
    return Path(path).read_text(encoding=encoding).splitlines(keepends=keepends)


def write_lines(
    path: str | Path,
    lines: Iterable[str],
    *,
    encoding: str = "utf-8",
    newline: str = "\n",
) -> None:
    """
    Write an iterable of lines to a file.

    Each provided line is written as-is; newline is inserted between lines.
    """
    p = Path(path)
    ensure_parent(p)
    payload = newline.join(list(lines))
    p.write_text(payload, encoding=encoding)


def normalize_newlines(text: str, *, newline: str = "\n") -> str:
    """
    Normalize mixed newlines (\r\n, \r, \n) to a single newline sequence.

    Useful for generated files where you want stable diffs across platforms.
    """
    # First collapse Windows and old-Mac newlines to \n, then re-expand to requested newline.
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if newline != "\n":
        normalized = normalized.replace("\n", newline)
    return normalized
