"""Architecture guards for ``openspec/specs/architecture/spec.md``.

Every guard parses the source with ``ast`` and never imports the modules it
checks. Each guard reports every offender, not only the first one.
"""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "src" / "ml_helper"
SHARED = "shared"


@dataclass(frozen=True)
class Module:
    path: Path
    name: str
    tree: ast.Module

    @property
    def is_package(self) -> bool:
        return self.path.name == "__init__.py"

    @property
    def layer(self) -> str | None:
        return _layer_of(self.name)

    @property
    def technique(self) -> str | None:
        return _technique_of(self.name)


def _modules(directory: Path = PACKAGE_DIR) -> list[Module]:
    modules = []
    for path in sorted(directory.rglob("*.py")):
        parts = path.relative_to(PACKAGE_DIR.parent).with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        modules.append(Module(path=path, name=".".join(parts), tree=tree))
    return modules


def _layer_of(name: str) -> str | None:
    parts = name.split(".")
    return parts[1] if parts[0] == "ml_helper" and len(parts) > 1 else None


def _technique_of(name: str) -> str | None:
    """Technique subpackage of an infrastructure or entrypoint name, if any."""
    parts = name.split(".")
    if _layer_of(name) in ("infrastructure", "entrypoints") and len(parts) > 2:
        return parts[2]
    return None


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


def test_dependencies_point_inward():
    allowed = {
        "core": {"core"},
        "infrastructure": {"core", "infrastructure"},
        "entrypoints": {"core", "infrastructure", "entrypoints"},
    }
    offenders = []
    for module in _modules():
        if module.layer not in allowed:
            continue
        for name in _imports(module):
            target = _layer_of(name)
            if target is not None and target not in allowed[module.layer]:
                offenders.append(f"{_relative(module.path)}: {module.layer} imports {name}")
    assert not offenders, (
        "Dependencies must point inward (architecture spec, 'Inward dependency "
        "direction'):\n" + "\n".join(offenders)
    )


def test_technique_infrastructure_is_isolated():
    offenders = []
    for module in _modules(PACKAGE_DIR / "infrastructure"):
        own = module.technique
        if own is None:
            continue
        for name in _imports(module):
            if _layer_of(name) != "infrastructure":
                continue
            target = _technique_of(name)
            if target is None or target in (own, SHARED):
                continue
            offenders.append(f"{_relative(module.path)}: {own} imports {target} ({name})")
    assert not offenders, (
        "Technique infrastructure may import only itself and 'shared' "
        "(architecture spec, 'Isolated technique infrastructure'):\n"
        + "\n".join(offenders)
    )


_COMPUTATION_NODES = (
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)
_AGGREGATING_CALLS = {"sum", "min", "max", "len", "sorted", "map", "filter"}
_COMPUTATION_IMPORTS = {"statistics"}


def test_core_performs_no_computation_over_collections():
    offenders = []
    for module in _modules(PACKAGE_DIR / "core"):
        where = _relative(module.path)
        for node in ast.walk(module.tree):
            if isinstance(node, _COMPUTATION_NODES):
                offenders.append(f"{where}:{node.lineno}: {type(node).__name__}")
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in _AGGREGATING_CALLS
            ):
                offenders.append(f"{where}:{node.lineno}: call to {node.func.id}()")
        for name in _imports(module):
            if name.split(".")[0] in _COMPUTATION_IMPORTS:
                offenders.append(f"{where}: imports {name}")
    assert not offenders, (
        "Core holds knowledge, not computation; move it to infrastructure behind "
        "a port (architecture spec, 'Core holds knowledge, not computation'):\n"
        + "\n".join(offenders)
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


def _has_core_module(technique: str) -> bool:
    core = PACKAGE_DIR / "core"
    return (core / f"{technique}.py").is_file() or (
        core / technique / "__init__.py"
    ).is_file()


def _defines_marimo_app(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "app" for t in node.targets)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "App"
        ):
            return True
    return False


def test_ml_helper_is_the_only_package_under_src():
    packages = _subpackages(ROOT / "src")
    assert packages == ["ml_helper"], (
        "Only 'ml_helper' may live under src/ (architecture spec, 'Three-layer "
        f"package'); found {packages}"
    )


def test_techniques_are_laid_out_consistently():
    infrastructure = PACKAGE_DIR / "infrastructure"
    entrypoints = PACKAGE_DIR / "entrypoints"
    offenders = []

    for technique in _subpackages(infrastructure):
        if technique != SHARED and not _has_core_module(technique):
            offenders.append(f"infrastructure/{technique}: no core module '{technique}'")

    for technique in _subpackages(entrypoints):
        if not _has_core_module(technique):
            offenders.append(f"entrypoints/{technique}: no core module '{technique}'")
        if not (infrastructure / technique / "pipeline.py").is_file():
            offenders.append(
                f"entrypoints/{technique}: no infrastructure/{technique}/pipeline.py"
            )
        notebook = entrypoints / technique / "notebook.py"
        if not notebook.is_file():
            offenders.append(f"entrypoints/{technique}: no notebook.py")
        elif not _defines_marimo_app(notebook):
            offenders.append(f"entrypoints/{technique}/notebook.py: defines no marimo app")

    assert not offenders, (
        "Techniques must use the same name in every layer; an entrypoint needs a "
        "core module, a pipeline, and a marimo notebook (architecture spec, "
        "'Technique layout across layers'):\n" + "\n".join(offenders)
    )
