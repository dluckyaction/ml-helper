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
