# project-baseline Specification

## Purpose

Platform repository baseline: hexagonal structure inherited by all future code, pure core without interface dependencies, installable packaging, valid OpenSpec configuration, and reference documentation.

## Requirements

### Requirement: Repository Hexagonal Structure

The project SHALL organize its source code under `src/` into three importable Python packages — `core`, `infrastructure`, and `entrypoints` — and tests under `tests/`.

#### Scenario: All three layer packages are importable

- **WHEN** running `uv run python -c "import core, infrastructure, entrypoints"`
- **THEN** the statement completes without import errors

#### Scenario: Directory structure exists

- **WHEN** inspecting the repository root
- **THEN** the directories `src/core/`, `src/infrastructure/`, `src/entrypoints/`, and `tests/` exist

### Requirement: Pure Core Without Interface Dependencies

The `src/core` layer SHALL remain in pure Python: no module inside `core` SHALL import Streamlit, Gradio, or FastAPI. The test suite SHALL automatically enforce this rule.

#### Scenario: Core purity guard

- **WHEN** running the test suite
- **THEN** a test executes and verifies that no file under `src/core/` imports `streamlit`, `gradio`, or `fastapi`

#### Scenario: Interface dependencies missing from core

- **WHEN** running the purity test on a `src/core` that contains a forbidden import of `streamlit`, `gradio`, or `fastapi`
- **THEN** the test fails and identifies the offending file

### Requirement: Project Packaging and Installation

The project SHALL be installable via `uv` from the repository, requiring Python 3.13 or higher, declaring runtime dependencies (`pandas`, `polars`, `pyarrow`, `pydantic`), and development dependencies (`pytest`).

#### Scenario: Editable installation and sync

- **WHEN** running `uv sync`
- **THEN** dependencies are installed cleanly and `pytest` becomes available in the environment

#### Scenario: Minimum Python version requirement

- **WHEN** inspecting `pyproject.toml`
- **THEN** `requires-python` is `>=3.13`

### Requirement: Valid OpenSpec Configuration

`openspec/config.yaml` SHALL be a valid YAML document defining the `context` (tech stack, domain, and architecture), `rules` (artifact rules), and `operations` (`apply` and `archive` guidance) sections.

#### Scenario: Configuration is readable by OpenSpec

- **WHEN** running `openspec doctor`
- **THEN** the configuration is parsed as valid YAML without errors

#### Scenario: Rules and operations defined

- **WHEN** reading `openspec/config.yaml`
- **THEN** `rules` contains the rule to end every task with a commit, and `operations.apply` contains the guidance to run `uv run pytest` before marking tasks as complete

### Requirement: Reference Documentation

`README.md` SHALL document the project purpose, technical stack, architecture (including the pure core rule), repository structure, and quickstart steps.

#### Scenario: Essential README content

- **WHEN** reading `README.md`
- **THEN** it contains the purpose, stack, pure core rule, and a quickstart installation/execution section

### Requirement: Executable Test Suite

Tests SHALL execute via `pytest` (`uv run pytest`) and include at least one import smoke test and the core purity guard.

#### Scenario: Green pytest status on baseline

- **WHEN** running `uv run pytest` at the repository root
- **THEN** the entire suite passes without errors