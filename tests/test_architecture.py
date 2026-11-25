"""Architecture guards for ``openspec/specs/architecture/spec.md``.

These guards protect the published knowledge and the portability of core:
standard-library core, knowledge docstring, and Knowledge catalog
(``project-baseline`` spec, "Executable Test Suite"). Other architecture rules
are enforced by review.

Every guard parses the source with ``ast`` and never imports the modules it
checks. Each guard reports every offender, not only the first one.
"""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "src" / "ml_helper"


@dataclass(frozen=True)
class Module:
    path: Path
    name: str
    tree: ast.Module

    @property
    def is_package(self) -> bool:
        return self.path.name == "__init__.py"


def _modules(directory: Path = PACKAGE_DIR) -> list[Module]:
    modules = []
    for path in sorted(directory.rglob("*.py")):
        parts = path.relative_to(PACKAGE_DIR.parent).with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        modules.append(Module(path=path, name=".".join(parts), tree=tree))
    return modules


def _imports(module: Module) -> list[str]:
    """Dotted names imported by ``module``, with relative imports resolved.

    ``from a import b`` yields ``a.b`` so that importing a subpackage by name
    is attributed to that subpackage.
    """
    names = []
    for node in ast.walk(module.tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                package = module.name.split(".")
                if not module.is_package:
                    package = package[:-1]
                base = package[: len(package) - (node.level - 1)]
                prefix = ".".join(base + ([node.module] if node.module else []))
            else:
                prefix = node.module
            names.extend(f"{prefix}.{alias.name}" for alias in node.names)
    return names


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def test_core_imports_only_the_standard_library():
    offenders = []
    for module in _modules(PACKAGE_DIR / "core"):
        for name in _imports(module):
            root = name.split(".")[0]
            if root == "ml_helper":
                continue
            if root not in sys.stdlib_module_names:
                offenders.append(f"{_relative(module.path)}: imports {name}")
    assert not offenders, (
        "Core may import only the standard library (architecture spec, "
        "'Standard-library core'):\n" + "\n".join(offenders)
    )


KNOWLEDGE_SECTIONS = [
    "Overview",
    "Definitions",
    "Method",
    "Assumptions and limitations",
    "References",
]


def _knowledge_problem(docstring: str | None) -> str | None:
    if not docstring:
        return "no module docstring"
    headings = [
        line.strip()[3:].strip()
        for line in docstring.splitlines()
        if line.strip().startswith("## ")
    ]
    missing = [section for section in KNOWLEDGE_SECTIONS if section not in headings]
    if missing:
        return "missing " + ", ".join(f"'## {section}'" for section in missing)
    found = [heading for heading in headings if heading in KNOWLEDGE_SECTIONS]
    if found != KNOWLEDGE_SECTIONS:
        return "sections out of order: " + ", ".join(found)
    return None


def test_core_modules_carry_a_knowledge_docstring():
    offenders = []
    for module in _modules(PACKAGE_DIR / "core"):
        if module.is_package:
            continue
        problem = _knowledge_problem(ast.get_docstring(module.tree))
        if problem:
            offenders.append(f"{_relative(module.path)}: {problem}")
    assert not offenders, (
        "Core modules need a knowledge docstring with "
        + ", ".join(f"'## {section}'" for section in KNOWLEDGE_SECTIONS)
        + " in this order (architecture spec, 'Knowledge docstring'):\n"
        + "\n".join(offenders)
    )


def _subpackages(directory: Path) -> list[str]:
    return sorted(
        child.name
        for child in directory.iterdir()
        if child.is_dir() and (child / "__init__.py").is_file()
    )


CATALOG_HEADING = "## Knowledge catalog"
CORE_MODULE_COLUMN = "Core module"


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _catalog_table() -> list[list[str]] | None:
    """Cells of the README catalog table, header first, or None without a catalog."""
    lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    if CATALOG_HEADING not in lines:
        return None
    table = []
    for line in lines[lines.index(CATALOG_HEADING) + 1 :]:
        if line.startswith("## "):
            break
        if line.startswith("|"):
            table.append(_cells(line))
    return table


def _core_module_names() -> set[str]:
    core = PACKAGE_DIR / "core"
    modules = {path.stem for path in core.glob("*.py") if path.name != "__init__.py"}
    return modules | set(_subpackages(core))


def test_every_core_module_is_in_the_catalog():
    table = _catalog_table()
    assert table is not None, f"README.md has no '{CATALOG_HEADING}' section"
    header = table[0] if table else []
    assert CORE_MODULE_COLUMN in header, (
        f"The README Knowledge catalog has no '{CORE_MODULE_COLUMN}' column "
        "(architecture spec, 'Knowledge catalog')"
    )
    column = header.index(CORE_MODULE_COLUMN)
    listed = {row[column].strip("`") for row in table[2:] if len(row) > column}
    missing = sorted(_core_module_names() - listed)
    assert not missing, (
        "Every core module needs a row in the README Knowledge catalog "
        "(architecture spec, 'Knowledge catalog'); missing: " + ", ".join(missing)
    )
