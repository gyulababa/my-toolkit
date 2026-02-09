# helpers/fs/paths.py
from __future__ import annotations

from pathlib import Path


def ensure_under_root(root: Path, candidate: Path) -> Path:
    root_path = Path(root).resolve(strict=False)
    candidate_path = Path(candidate).resolve(strict=False)

    try:
        candidate_path.relative_to(root_path)
    except ValueError as e:
        raise ValueError(f"Path escapes root: {candidate_path}") from e

    return candidate_path


def join_safe(root: Path, *parts: str) -> Path:
    for part in parts:
        if Path(part).is_absolute():
            raise ValueError(f"Absolute path part not allowed: {part}")

    candidate = Path(root).joinpath(*parts)
    return ensure_under_root(root, candidate)
