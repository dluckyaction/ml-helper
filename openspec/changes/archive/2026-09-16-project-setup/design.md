# Design: Repository Baseline (Task 0)

## Context

The repository is empty: only `openspec/config.yaml` (currently invalid YAML) and `.opencode/` exist.

Mandatory technical environment: Python 3.13+, `uv`, Pandas, Polars, PyArrow, Pydantic, Pytest. Hexagonal/clean architecture with a strict pure core rule in `src/core` (zero imports of Streamlit/Gradio/FastAPI). Container-ready deployment, executable via CLI or service.

## Goals / Non-Goals

**Goals:**
- Installable and verifiable skeleton initialized with `uv`: structure, packaging, OpenSpec config, passing green tests.
- Ensure `openspec doctor` passes (valid config) and `uv run pytest` passes on the baseline.
- Operationalize architectural rules (pure core) via an automated AST test guard.

**Non-Goals:**
- Do not include Dockerfile or compose setup yet.
- Do not include concrete entrypoints (CLI, FastAPI, Streamlit) or domain logic.
- Do not add code quality tools (ruff/mypy) or CI in this baseline.

## Decisions

### 1. `src/` Layout with Layer Packages `core`, `infrastructure`, `entrypoints`

Use a `src` layout with top-level packages matching the layers:

src/
  core/            # pure domain: models, metrics, ports (Protocol)
  infrastructure/  # adapters: I/O, connectors, persistence
  entrypoints/     # UI/API/CLI (empty placeholders for now)
  __init__.py      # each layer is an importable package
  tests/


- Direct imports: `from core import ...`, `from infrastructure import ...`.
- Each package is created with `__init__.py` to be immediately importable.

### 2. Operationalized Pure Core Rule

`src/core` allows only stdlib, Pydantic (models/validation), and PyArrow (tabular interchange).
Pandas and Polars live in `infrastructure` as adapters.

- **Purity Guard**: A test in `tests/` parses all files in `src/core` using `ast` (stdlib) and fails if it encounters any top-level import of `streamlit`, `gradio`, or `fastapi`.

### 3. `pyproject.toml` — `uv` Packaging and Dependencies

- Project initialized with `uv init`, declaring `src` layout.
- `requires-python = ">=3.13"`.
- `[project.dependencies]`: `pandas`, `polars`, `pyarrow`, `pydantic`.
- `[project.optional-dependencies] dev = ["pytest"]`, and `testpaths = ["tests"]` under `[tool.pytest.ini_options]`.

### 4. `openspec/config.yaml` — Valid Configuration

Rewrite the file as valid YAML:
- `schema: spec-driven`.
- `context`: technical stack (Python 3.13+, `uv`), domain, hexagonal architecture, pure core rule, container-ready deployment, and English language rule for all OpenSpec artifacts.
- `rules`: `tasks: end every task with a commit`.
- `operations`:
  - `apply.guidance`: run `uv run pytest` before marking tasks complete.
  - `archive.guidance`: summarize results before archiving.

### 5. Reference README.md

Sections: purpose, stack, architecture (ASCII diagram + pure core rule), repository structure, quickstart (`uv sync`, `uv run pytest`), and OpenSpec workflow reference.

## Risks / Trade-offs

- **[Generic package names (`core`, `entrypoints`)]** → Mitigated by `src` layout.
- **[Purity guard false positives]** → Mitigated by using `ast` parsing instead of raw string checks.

## Migration Plan

Greenfield repo. Revert condition: `openspec doctor` and `uv run pytest` must pass bef