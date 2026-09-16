"""Core purity guard: src/core must not import UI/framework libraries."""

import ast
from pathlib import Path

FORBIDDEN_IMPORTS = {"streamlit", "gradio", "fastapi"}

CORE_DIR = Path(__file__).resolve().parents[1] / "src" / "core"


def _imported_module_roots(tree):
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.add(node.module.split(".")[0])
    return roots


def _core_python_files():
    return sorted(CORE_DIR.rglob("*.py"))


def test_core_is_pure():
    offenders = []
    for path in _core_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported = _imported_module_roots(tree)
        violations = imported & FORBIDDEN_IMPORTS
        if violations:
            offenders.append(f"{path}: {sorted(violations)}")
    assert not offenders, "Forbidden imports found in src/core:\n" + "\n".join(offenders)