# tests/test_architecture_imports.py
from __future__ import annotations

import ast
from pathlib import Path


def _find_catalogloader_imports(root: Path) -> list[tuple[Path, int, str]]:
    violations: list[tuple[Path, int, str]] = []
    for path in root.rglob("*.py"):
        if "catalogloader" in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if name == "helpers.catalogloader" or name.startswith("helpers.catalogloader."):
                        line = source.splitlines()[node.lineno - 1].rstrip()
                        violations.append((path, node.lineno, line))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "helpers.catalogloader" or module.startswith("helpers.catalogloader."):
                    line = source.splitlines()[node.lineno - 1].rstrip()
                    violations.append((path, node.lineno, line))
                elif module == "helpers":
                    for alias in node.names:
                        if alias.name == "catalogloader":
                            line = source.splitlines()[node.lineno - 1].rstrip()
                            violations.append((path, node.lineno, line))
    return violations


def test_helpers_do_not_import_catalogloader() -> None:
    root = Path(__file__).resolve().parents[1] / "helpers"
    violations = _find_catalogloader_imports(root)
    assert not violations, "helpers/* imports helpers.catalogloader:\n" + "\n".join(
        f"{path}:{lineno} {line}" for path, lineno, line in violations
    )


def _find_forbidden_imports(root: Path, forbidden: list[str]) -> list[tuple[Path, int, str, str]]:
    violations: list[tuple[Path, int, str, str]] = []
    forbidden_lower = [item.lower() for item in forbidden]
    for path in root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    name_lower = name.lower()
                    for item in forbidden_lower:
                        if item in name_lower:
                            line = source.splitlines()[node.lineno - 1].rstrip()
                            violations.append((path, node.lineno, item, line))
                            break
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                module_lower = module.lower()
                for item in forbidden_lower:
                    if item in module_lower:
                        line = source.splitlines()[node.lineno - 1].rstrip()
                        violations.append((path, node.lineno, item, line))
                        break
                if module == "":
                    for alias in node.names:
                        name = alias.name
                        name_lower = name.lower()
                        for item in forbidden_lower:
                            if item in name_lower:
                                line = source.splitlines()[node.lineno - 1].rstrip()
                                violations.append((path, node.lineno, item, line))
                                break
    return violations


def test_helpers_do_not_import_ui_frameworks_or_services() -> None:
    root = Path(__file__).resolve().parents[1] / "helpers"
    forbidden = [
        "dearpygui",
        "pyside",
        "qt",
        "tkinter",
        "preview_vision",
        "services",
        "requests",
        "subprocess",
    ]
    violations = _find_forbidden_imports(root, forbidden)
    assert not violations, "helpers/* imports forbidden modules:\n" + "\n".join(
        f"{path}:{lineno} [{item}] {line}" for path, lineno, item, line in violations
    )
