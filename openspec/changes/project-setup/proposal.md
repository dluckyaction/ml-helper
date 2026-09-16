# Proposal: Repository Baseline (Task 0)

## Why

The repository is currently empty (containing only `openspec/config.yaml` and `.opencode/`), and the current `openspec/config.yaml` is invalid YAML: `openspec doctor` cannot parse it.
Task 0 establishes the foundation upon which the entire platform will be built — hexagonal structure, packaging, OpenSpec configuration, and baseline documentation — using `uv` as the package manager and targeting Python 3.13+.

## What Changes

- Fixes and completes `openspec/config.yaml`: valid `context` (tech stack with Python 3.13+, domain, architecture, pure core rule, container-ready deployment), and `operations` (`apply`/`archive` guidance, including running `uv run pytest` before marking tasks complete).
- Initializes the project using `uv init` with Python 3.13+.
- Creates the Python package structure: `src/core/`, `src/infrastructure/`, `src/entrypoints/` (`src` layout) and `tests/`.
- Configures `pyproject.toml` with dependencies: `pandas`, `polars`, `pyarrow`, `pydantic`, and `dev` extra with `pytest`.
- Creates a reference `README.md`: purpose, stack, architecture, repository structure, and quickstart guide with `uv`.
- Adds a baseline smoke test and a core purity test (`src/core` without imports from `streamlit`, `gradio`, or `fastapi`), verifiable via `uv run pytest`.
- **BREAKING**: None. Greenfield repository with no existing code.

## Capabilities

### New Capabilities

- `project-baseline`: Core rules and baseline repository structure inherited by the entire platform: hexagonal layout, pure core without UI/framework dependencies, OpenSpec configuration, `uv`-based packaging, and reference documentation.

### Modified Capabilities

- None (no existing capabilities).

## Impact

- **Code**: New repository setup. Packages `core`, `infrastructure`, and `entrypoints` are created under `src/`.
- **Configuration**: `openspec/config.yaml` is rewritten; ensures `openspec doctor` passes cleanly.
- **Dependencies**: Managed via `uv`: `pandas`, `polars`, `pyarrow`, `pydantic`; `dev` extra with `pytest`.
- **Tooling**: `uv` for package management and `pytest` as the test runner.
- **Out of Scope**: Dockerfile/`docker-compose`, concrete entrypoints (CLI, FastAPI, Streamlit), domain logic.


