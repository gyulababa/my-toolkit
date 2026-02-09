# tests/test_persist_boundary.py
from __future__ import annotations

import ast
from pathlib import Path


MARKERS = ("index.json", "active_id", "next_int", "persist_root")


def _iter_string_literals(tree: ast.AST) -> list[tuple[int, str]]:
    literals: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.append((node.lineno, node.value))
        elif isinstance(node, ast.JoinedStr):
            for part in node.values:
                if isinstance(part, ast.Constant) and isinstance(part.value, str):
                    literals.append((part.lineno, part.value))
    return literals


def _is_allowed(path: Path) -> bool:
    parts = path.parts
    if "tests" in parts:
        return True
    if "helpers" in parts:
        helpers_idx = parts.index("helpers")
        if len(parts) > helpers_idx + 1 and parts[helpers_idx + 1] in {"persist", "catalogloader"}:
            return True
    return False


def test_persist_markers_confined_to_persist_modules() -> None:
    root = Path(__file__).resolve().parents[1]
    violations: list[tuple[Path, int, str, str]] = []
    for path in root.rglob("*.py"):
        if _is_allowed(path):
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for lineno, text in _iter_string_literals(tree):
            for marker in MARKERS:
                if marker in text:
                    line = source.splitlines()[lineno - 1].rstrip()
                    violations.append((path, lineno, marker, line))
    assert not violations, "persist markers found outside helpers/persist or helpers/catalogloader:\n" + "\n".join(
        f"{path}:{lineno} [{marker}] {line}" for path, lineno, marker, line in violations
    )
