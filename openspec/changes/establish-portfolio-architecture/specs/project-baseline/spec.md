# Spec Delta

## MODIFIED Requirements

### Requirement: Repository Hexagonal Structure

The project SHALL organize its source code under `src/ml_helper/` into three importable subpackages — `core`, `infrastructure`, and `entrypoints` — and tests under `tests/`. The rules governing each layer are defined by the `architecture` capability.

#### Scenario: All three layer packages are importable

- **WHEN** running `uv run python -c "import ml_helper.core, ml_helper.infrastructure, ml_helper.entrypoints"`
- **THEN** the statement completes without import errors

#### Scenario: Directory structure exists

- **WHEN** inspecting the repository root
- **THEN** the directories `src/ml_helper/core/`, `src/ml_helper/infrastructure/`, `src/ml_helper/entrypoints/`, and `tests/` exist

### Requirement: Project Packaging and Installation

The project SHALL be installable via `uv` from the repository, requiring Python 3.13 or higher, building the single package `ml_helper`, declaring the platform runtime dependencies (`pandas`, `polars`, `pyarrow`, `marimo`, `altair`), and development dependencies (`pytest`). Dependencies used by a single technique SHALL follow the `architecture` capability's rule on technique-exclusive dependencies.

#### Scenario: Editable installation and sync

- **WHEN** running `uv sync`
- **THEN** dependencies are installed cleanly and `pytest` becomes available in the environment

#### Scenario: Minimum Python version requirement

- **WHEN** inspecting `pyproject.toml`
- **THEN** `requires-python` is `>=3.13`

#### Scenario: Unused dependencies are not declared

- **WHEN** inspecting the runtime dependencies in `pyproject.toml`
- **THEN** `pydantic` is not listed

### Requirement: Reference Documentation

`README.md` SHALL document the project purpose as a portfolio of machine learning techniques, the technical stack, a summary of the architecture linking to the `architecture` specification, the repository structure, the technique catalog, and quickstart steps.

#### Scenario: Essential README content

- **WHEN** reading `README.md`
- **THEN** it contains the purpose, stack, an architecture summary linking to `openspec/specs/architecture/spec.md`, the technique catalog, and a quickstart installation/execution section

### Requirement: Executable Test Suite

Tests SHALL execute via `pytest` (`uv run pytest`) and include at least one import smoke test and the architecture guards required by the `architecture` capability (dependency direction, standard-library core, computation, knowledge docstring, layout, and catalog).

#### Scenario: Green pytest status on baseline

- **WHEN** running `uv run pytest` at the repository root
- **THEN** the entire suite passes without errors

#### Scenario: Architecture guards are part of the suite

- **WHEN** listing the collected tests
- **THEN** the suite contains the architecture guards

## REMOVED Requirements

### Requirement: Pure Core Without Interface Dependencies

**Reason**: Superseded by the stricter `Standard-library core` requirement of the `architecture` capability, which allowlists the standard library instead of blacklisting three UI frameworks.

**Migration**: The blacklist guard in `tests/test_core_purity.py` is replaced by the standard-library allowlist guard in the architecture test suite.
